"""
Vues pour la gestion des tiers d'utilisateurs par les administrateurs
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone

from main.models.User import User
from main.models.UserTier import UserTier
from main.enum.PermissionEnum import PermissionEnum
from main.utils.ExtractPaginator import extract_context_to_paginator
from main.utils.UserTierManager import UserTierManager
from main.utils.ServerNotificationBuilder import ServerNotificationBuilder



@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def admin_user_tiers_dashboard(request) -> HttpResponse:
    """Dashboard de gestion des tiers d'utilisateurs"""
    
    # Statistiques des tiers
    tier_stats = {}
    for tier_name, tier_info in UserTierManager.get_all_tiers().items():
        count = UserTier.objects.filter(tier_name=tier_name).count()
        tier_stats[tier_name] = {
            'count': count,
            'display_name': tier_info['display_name']
        }
    
    # Abonnements expirant bientôt (dans les 7 jours)
    expiry_threshold = timezone.now() + timedelta(days=7)
    expiring_soon = UserTier.objects.filter(
        tier_expiry_date__lte=expiry_threshold,
        tier_expiry_date__gte=timezone.now(),
    ).count()
    
    # Abonnements expirés
    expired = UserTier.objects.filter(
        tier_expiry_date__lt=timezone.now(),
    ).count()
    
    context = {
        'tier_stats': tier_stats,
        'expiring_soon': expiring_soon,
        'expired': expired,
        'tier_comparison': UserTierManager.get_tier_comparison()
    }
    
    return render(request, 'Html/Manager/user_tiers_dashboard.html', context)


@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def admin_user_tiers_listing(request) -> HttpResponse:
    """Liste des utilisateurs avec leurs tiers"""
    
    page_number = int(request.GET.get('page', 1))
    search = request.GET.get('search', '')
    tier_filter = request.GET.get('tier', '')
    
    queryset = UserTier.objects.select_related('user').all()
    
    # Filtres
    if search:
        queryset = queryset.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    if tier_filter:
        queryset = queryset.filter(tier_name=tier_filter)
    
    queryset = queryset.order_by('-tier_start_date')
    
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    
    # Ajouter les options de filtre
    context.update({
        'search': search,
        'tier_filter': tier_filter,
        'tier_choices': [(tier, info['display_name']) for tier, info in UserTierManager.get_all_tiers().items()],
    })
    
    return render(request, 'Html/Manager/user_tiers_listing.html', context)


@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET', 'POST'])
def manager_user_tier_edit(request, user_uuid) -> HttpResponse:
    """Édition du tier d'un utilisateur"""
    
    user = get_object_or_404(User, uuid=user_uuid)
    user_tier, _ = UserTier.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        try:
            new_tier = request.POST.get('tier_name')
            expiry_date = request.POST.get('tier_expiry_date')
            payment_reference = request.POST.get('payment_reference', '')
            notes = request.POST.get('notes', '')
            auto_renew = request.POST.get('auto_renew') == 'on'
            
            # Validation
            if new_tier not in UserTierManager.get_all_tiers():
                ServerNotificationBuilder(request).set_message('Tier invalide sélectionné').set_statut("error").send()
                return redirect('adminUserTierEdit', user_uuid=user_uuid)
            
            # Conversion de la date d'expiration
            parsed_expiry = None
            if expiry_date:
                try:
                    parsed_expiry = datetime.strptime(expiry_date, '%Y-%m-%d').date()
                    parsed_expiry = timezone.make_aware(
                        datetime.combine(parsed_expiry, datetime.min.time())
                    )
                except ValueError:
                    ServerNotificationBuilder(request).set_message('Format de date invalide').set_statut("error").send()
                    return redirect('adminUserTierEdit', user_uuid=user_uuid)
            
            # Mise à jour du tier
            user_tier.upgrade_tier(
                new_tier, 
                parsed_expiry, 
                payment_reference, 
                changed_by=request.user,
                change_reason='ADMIN_CHANGE'
            )
            user_tier.notes = notes
            user_tier.auto_renew = auto_renew
            

            user_tier.save()

            ServerNotificationBuilder(request).set_message(f'Tier de {user.username} mis à jour avec succès').set_statut("success").send()
            return redirect('adminUserTiersListing')
            
        except Exception as e:
            ServerNotificationBuilder(request).set_message(f'Erreur lors de la mise à jour: {str(e)}').set_statut("error").send()

    context = {
        'user': user,
        'user_tier': user_tier,
        'tier_choices': json.dumps(UserTierManager.get_all_tiers()),
        'tier_choices_form': UserTierManager.get_all_tiers(),
        'current_limits': user_tier.get_effective_limits() if user_tier else UserTierManager.get_tier_limits('STANDARD')
    }
    
    return render(request, 'Html/Manager/user_tier_edit.html', context)


@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['POST'])
def manager_user_tier_bulk_action(request) -> HttpResponse:
    """Actions en lot sur les tiers d'utilisateurs"""
    
    action = request.POST.get('action')
    user_ids = request.POST.getlist('user_ids')
    
    if not action or not user_ids:
        ServerNotificationBuilder(request).set_message('Action ou utilisateurs non spécifiés').set_statut("error").send()
        return redirect('adminUserTiersListing')
    
    try:
        users = User.objects.filter(uuid__in=user_ids)
        
        if action == 'downgrade_to_standard':
            for user in users:
                user_tier, _ = UserTier.objects.get_or_create(user=user)
                user_tier.downgrade_to_standard()
            ServerNotificationBuilder(request).set_message(f'{len(users)} utilisateur(s) rétrogradé(s) au tier Standard').set_statut("success").send()
        elif action == 'extend_subscription':
            days = int(request.POST.get('extend_days', 30))
            for user in users:
                user_tier, _ = UserTier.objects.get_or_create(user=user)
                if user_tier.tier_expiry_date:
                    user_tier.tier_expiry_date += timedelta(days=days)
                else:
                    user_tier.tier_expiry_date = timezone.now() + timedelta(days=days)
                user_tier.save()

            ServerNotificationBuilder(request).set_message(f'Abonnement étendu de {days} jours pour {len(users)} utilisateur(s)').set_statut("success").send()
        else:
            ServerNotificationBuilder(request).set_message('Action non reconnue').set_statut("error").send()
    except Exception as e:
        ServerNotificationBuilder(request).set_message(f'Erreur lors de l\'action en lot: {str(e)}').set_statut("error").send()
    return redirect('adminUserTiersListing')


@login_required
@permission_required('auth.' + PermissionEnum.MANAGER_ACCESS_DASHBOARD.name, login_url='login')
@require_http_methods(['GET'])
def manager_user_tiers_expiring(request) -> HttpResponse:
    """Liste des abonnements expirant bientôt"""
    
    page_number = int(request.GET.get('page', 1))
    days_ahead = int(request.GET.get('days', settings.TIER_EXPIRATION_WARNING_DAYS))
    
    expiry_threshold = timezone.now() + timedelta(days=days_ahead)
    
    queryset = UserTier.objects.filter(
        tier_expiry_date__lte=expiry_threshold,
    ).select_related('user').order_by('tier_expiry_date')
    
    paginator = Paginator(queryset, 50)
    context = extract_context_to_paginator(paginator, page_number)
    context['days_ahead'] = days_ahead
    
    return render(request, 'Html/Manager/user_tiers_expiring.html', context)
