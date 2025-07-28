import uuid
from django.db import models
from django.conf import settings
from encrypted_model_fields.fields import EncryptedCharField
from home.models.UserTierHistory import UserTierHistory
from django.utils import timezone
from home.utils.UserTierManager import UserTierManager



class UserTier(models.Model):
    """Modèle pour stocker les informations de tier des utilisateurs"""
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user = models.OneToOneField(
        'User', 
        on_delete=models.CASCADE, 
        related_name='tier_info'
    )
    
    tier_name = models.CharField(
        max_length=50,
        choices=[
            ('STANDARD', 'Standard'),
            ('PREMIUM_BASIC', 'Premium Basic'),
            ('PREMIUM_ADVANCED', 'Premium Advanced'),
            ('PREMIUM_PRO', 'Premium Pro'),
        ],
        default='STANDARD',
        help_text="Tier actuel de l'utilisateur"
    )
    
    tier_start_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de début du tier actuel"
    )
    
    tier_expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date d'expiration du tier (pour les abonnements premium)"
    )
    
    auto_renew = models.BooleanField(
        default=False,
        help_text="Renouvellement automatique de l'abonnement"
    )
    
    # Informations de facturation
    payment_reference = EncryptedCharField(
        max_length=255,
        blank=True,
        help_text="Référence de paiement ou ID de transaction"
        
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes administratives sur le tier de l'utilisateur"
    )

    class Meta:
        ordering = ['-tier_start_date']
        verbose_name = "Tier Utilisateur"
        verbose_name_plural = "Tiers Utilisateurs"

    def __str__(self):
        return f"{self.user.username} - {self.get_tier_name_display()}"
    

    def get_effective_limits(self):
        """Retourne les limites effectives (custom ou tier par défaut)"""
        
        default_limits = UserTierManager.get_tier_limits(self.tier_name)
        
        return {
            'soundboard':  default_limits['soundboard'],
            'playlist': default_limits['playlist'],
            'music_per_playlist': default_limits['music_per_playlist'],
            'weight_music_mb': default_limits['weight_music_mb'],
        }
        
        
    
    def is_premium(self):
        """Retourne True si l'utilisateur a un tier premium"""
        return self.tier_name != 'STANDARD'
    
    def is_subscription_expired(self):
        """Vérifie si l'abonnement a expiré"""
        if not self.tier_expiry_date:
            return False
        
        return timezone.now() > self.tier_expiry_date
    
    def get_days_until_expiry(self):
        """Retourne le nombre de jours avant l'expiration"""
        if not self.tier_expiry_date:
            return None
        
        delta = self.tier_expiry_date - timezone.now()
        return delta.days
    
    def upgrade_tier(self, new_tier, expiry_date=None, payment_reference=None, changed_by=None, change_reason='UPGRADE'):
        """Met à jour le tier de l'utilisateur avec historique"""
        
        old_tier = self.tier_name
        
        # Créer l'historique avant le changement
        UserTierHistory.objects.create(
            user=self.user,
            previous_tier=old_tier,
            new_tier=new_tier,
            change_reason=change_reason,
            changed_by=changed_by,
            payment_reference=payment_reference,
            tier_start_date=timezone.now(),
            tier_end_date=expiry_date,
            tier_duration_days=(expiry_date - timezone.now()).days if expiry_date else None
        )
        
        # Mettre à jour le tier
        self.previous_tier = old_tier
        self.tier_name = new_tier
        self.tier_expiry_date = expiry_date
        self.payment_reference = payment_reference or self.payment_reference
        self.tier_start_date = timezone.now()
        
        self.save()
    
    def downgrade_to_standard(self, changed_by=None, change_reason='DOWNGRADE'):
        """Rétrograde l'utilisateur au tier standard avec historique"""

        
        old_tier = self.tier_name
        
        # Créer l'historique avant le changement
        UserTierHistory.objects.create(
            user=self.user,
            previous_tier=old_tier,
            new_tier='STANDARD',
            change_reason=change_reason,
            changed_by=changed_by,
            tier_start_date=timezone.now(),
            notes=f"Downgrade automatique de {old_tier} vers STANDARD"
        )
        
        # Mettre à jour le tier
        self.previous_tier = old_tier
        self.tier_name = 'STANDARD'
        self.tier_expiry_date = None
        self.auto_renew = False
        self.tier_start_date = timezone.now()
        
        self.save()
