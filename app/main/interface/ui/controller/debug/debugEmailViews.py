import uuid
from types import SimpleNamespace

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _, get_language, override
from django.views.decorators.http import require_http_methods

from main.architecture.persistence.models.User import User
from main.domain.common.utils.EmailSender import EmailSender
from main.domain.common.utils.settings import Settings


def _ensure_debug_mode() -> None:
    if not settings.DEBUG:
        raise Http404()


def _render_email(template_name: str, context: dict) -> str:
    language = get_language() or 'fr'
    with override(language):
        return render_to_string(template_name, context)


def _send_email(recipient_email: str, subject_key: str, template_name: str, context: dict) -> None:
    subject = _(subject_key)
    html_content = _render_email(template_name, context)
    EmailSender().send_email(subject, html_content, Settings.get('EMAIL_NO_REPLY'), [recipient_email])


def _build_report_context(user: User) -> dict:
    report = SimpleNamespace(
        typeElement='soundboard',
        precisionElement='text',
        descriptionElement='Signalement de debug pour tester MailHog.',
        created_at=timezone.now(),
        creator=user,
        uuidElement=uuid.uuid4(),
    )
    return {'report': report, 'title': _('template.email.moderator.reported.subject')}


def _send_confirmation_email(user: User, recipient_email: str) -> None:
    confirmation_token = uuid.uuid4()
    confirmation_url = reverse(
        'confirm_account',
        kwargs={'uuid_user': user.uuid, 'confirmation_token': confirmation_token},
    )
    _send_email(
        recipient_email,
        'template.email.user.confirm.subject',
        'EmailTemplate/user/confirmEmail.html',
        {
            'title': _('template.email.user.confirm.subject'),
            'user': user,
            'url': confirmation_url,
        },
    )


def _send_reset_password_email(user: User, recipient_email: str) -> None:
    reset_token = uuid.uuid4().hex
    reset_url = reverse(
        'token_validation_reset_password',
        kwargs={'uuid_user': user.uuid, 'token_reinitialisation': reset_token},
    )
    _send_email(
        recipient_email,
        'template.email.user.reset_password.subject',
        'EmailTemplate/user/resetPassword.html',
        {
            'title': _('template.email.user.reset_password.subject'),
            'user': user,
            'url': reset_url,
        },
    )


def _send_reported_content_email(user: User, recipient_email: str) -> None:
    _send_email(
        recipient_email,
        'template.email.moderator.reported.subject',
        'EmailTemplate/moderator/contentReported.html',
        _build_report_context(user),
    )


def _get_debug_actions():
    return [
        {
            'key': 'welcome',
            'label': 'Email de bienvenue',
            'description': 'Envoie le message de bienvenue avec le template HTML réel.',
        },
        {
            'key': 'confirm',
            'label': 'Email de confirmation',
            'description': 'Envoie le mail de confirmation avec un lien de test.',
        },
        {
            'key': 'reset_password',
            'label': 'Réinitialisation de mot de passe',
            'description': 'Envoie le mail de réinitialisation avec un lien de test.',
        },
        {
            'key': 'password_changed',
            'label': 'Mot de passe modifié',
            'description': 'Envoie l’email de notification de changement de mot de passe.',
        },
        {
            'key': 'account_auto_deletion',
            'label': 'Suppression automatique de compte',
            'description': 'Envoie le mail de suppression après 24 mois.',
        },
        {
            'key': 'account_auto_deletion_never_login',
            'label': 'Suppression sans connexion',
            'description': 'Envoie le mail de suppression pour compte jamais utilisé.',
        },
        {
            'key': 'prevent_account_deletion',
            'label': 'Prévenir la suppression',
            'description': 'Envoie le mail d’avertissement avant suppression.',
        },
        {
            'key': 'prevent_account_auto_deletion_never_confirmed',
            'label': 'Prévenir la suppression non confirmée',
            'description': 'Envoie le mail d’avertissement pour compte non confirmé.',
        },
        {
            'key': 'account_auto_deletion_never_confirmed',
            'label': 'Suppression non confirmée',
            'description': 'Envoie le mail de suppression pour compte non confirmé.',
        },
        {
            'key': 'tiers_downgrade_notification',
            'label': 'Rétrogradation de tier',
            'description': 'Envoie la notification de rétrogradation de tier.',
        },
        {
            'key': 'tiers_expiration_warning',
            'label': 'Avertissement d’expiration de tier',
            'description': 'Envoie l’email d’alerte avant expiration.',
        },
        {
            'key': 'reported_content',
            'label': 'Signalement modérateur',
            'description': 'Envoie l’email de signalement modérateur avec un faux signalement.',
        },
    ]


def _send_action(action_key: str, user: User, recipient_email: str) -> None:
    if action_key == 'welcome':
        _send_email(
            recipient_email,
            'template.email.user.welcome.subject',
            'EmailTemplate/user/welcomEmail.html',
            {
                'title': _('template.email.user.welcome.subject'),
                'user': user,
            },
        )
    elif action_key == 'confirm':
        _send_confirmation_email(user, recipient_email)
    elif action_key == 'reset_password':
        _send_reset_password_email(user, recipient_email)
    elif action_key == 'password_changed':
        _send_email(
            recipient_email,
            'template.email.user.password_changed.subject',
            'EmailTemplate/user/password_changed.html',
            {
                'title': _('template.email.user.password_changed.subject'),
                'user': user,
            },
        )
    elif action_key == 'account_auto_deletion':
        _send_email(
            recipient_email,
            'template.email.user.account_deleted.subject',
            'EmailTemplate/user/autoDeletionAccount.html',
            {
                'title': _('template.email.user.account_deleted.subject'),
                'user': user,
            },
        )
    elif action_key == 'account_auto_deletion_never_login':
        _send_email(
            recipient_email,
            'template.email.user.account_deleted.subject',
            'EmailTemplate/user/autoDeletionAccountNeverLogin.html',
            {
                'title': _('template.email.user.account_deleted.subject'),
                'user': user,
            },
        )
    elif action_key == 'prevent_account_deletion':
        _send_email(
            recipient_email,
            'template.email.user.prevent_deletion.subject',
            'EmailTemplate/user/preventAutoDeletion.html',
            {
                'title': _('template.email.user.prevent_deletion.subject'),
                'user': user,
            },
        )
    elif action_key == 'prevent_account_auto_deletion_never_confirmed':
        _send_email(
            recipient_email,
            'template.email.user.prevent_deletion_unconfirmed.subject',
            'EmailTemplate/user/preventAutoDeletionNotConfirmed.html',
            {
                'title': _('template.email.user.prevent_deletion_unconfirmed.subject'),
                'user': user,
                'url': reverse('confirm_account', kwargs={'uuid_user': user.uuid, 'confirmation_token': uuid.uuid4()}),
            },
        )
    elif action_key == 'account_auto_deletion_never_confirmed':
        _send_email(
            recipient_email,
            'template.email.user.account_deleted_unconfirmed.subject',
            'EmailTemplate/user/autoDeletionNotConfirmed.html',
            {
                'title': _('template.email.user.account_deleted_unconfirmed.subject'),
                'user': user,
            },
        )
    elif action_key == 'tiers_downgrade_notification':
        _send_email(
            recipient_email,
            'template.email.user.tier_downgrade.subject',
            'EmailTemplate/user/tierDowngradeNotification.html',
            {
                'title': _('template.email.user.tier_downgrade.subject'),
                'user': user,
                'new_tier': 'Debug',
            },
        )
    elif action_key == 'tiers_expiration_warning':
        _send_email(
            recipient_email,
            'template.email.user.tier_expiration.subject',
            'EmailTemplate/user/tierExpirationWarning.html',
            {
                'title': _('template.email.user.tier_expiration.subject'),
                'user': user,
                'days_left': 7,
            },
        )
    elif action_key == 'reported_content':
        _send_reported_content_email(user, recipient_email)
    else:
        raise ValueError(f'Unknown debug email action: {action_key}')


@login_required
@require_http_methods(['GET', 'POST'])
def debug_email_test(request: HttpRequest) -> HttpResponse:
    _ensure_debug_mode()

    if not request.user.email:
        messages.error(request, 'Votre compte doit avoir une adresse email pour tester les mails.')

    actions = _get_debug_actions()

    if request.method == 'POST' and request.user.email:
        action_key = request.POST.get('action', 'all')
        selected_actions = actions if action_key == 'all' else [action for action in actions if action['key'] == action_key]
        sent_count = 0
        for action in selected_actions:
            try:
                _send_action(action['key'], request.user, request.user.email)
                sent_count += 1
            except Exception as exc:
                messages.error(request, f"{action['label']} : {exc}")
        if sent_count:
            messages.success(request, f"{sent_count} email(s) envoyé(s) vers {request.user.email}.")

    return render(
        request,
        'Html/Debug/email_test.html',
        {
            'title': 'Debug emails',
            'actions': actions,
            'recipient_email': request.user.email,
            'debug_enabled': settings.DEBUG,
        },
    )