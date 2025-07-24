import uuid
from django.db import models


class UserTierHistory(models.Model):
    """Historique des changements de tiers d'utilisateurs"""
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='tier_history'
    )
    
    # Changement de tier
    previous_tier = models.CharField(
        max_length=50,
        help_text="Tier précédent"
    )
    
    new_tier = models.CharField(
        max_length=50,
        help_text="Nouveau tier"
    )
    
    # Métadonnées du changement
    change_reason = models.CharField(
        max_length=255,
        choices=[
            ('UPGRADE', 'Upgrade payant'),
            ('DOWNGRADE', 'Downgrade/Expiration'),
            ('ADMIN_CHANGE', 'Modification administrative'),
            ('MIGRATION', 'Migration système'),
            ('PROMO', 'Promotion/Offre spéciale'),
        ],
        help_text="Raison du changement de tier"
    )
    
    # Qui a effectué le changement
    changed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tier_changes_made',
        help_text="Utilisateur ayant effectué le changement (admin/système)"
    )
    
    # Informations de paiement (si applicable)
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        help_text="Référence de paiement associée"
    )
    
    payment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Montant payé pour ce changement"
    )
    
    # Durée et dates
    tier_duration_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Durée du tier en jours"
    )
    
    tier_start_date = models.DateTimeField(
        help_text="Date de début du nouveau tier"
    )
    
    tier_end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de fin prévue du tier"
    )
    
    # Notes administratives
    notes = models.TextField(
        blank=True,
        help_text="Notes sur ce changement de tier"
    )
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Adresse IP lors du changement"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User agent lors du changement"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Historique Tier Utilisateur"
        verbose_name_plural = "Historiques Tiers Utilisateurs"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['change_reason']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.previous_tier} → {self.new_tier} ({self.get_change_reason_display()})"

    @property
    def is_upgrade(self):
        """Indique si c'est un upgrade vers un tier supérieur"""
        tier_hierarchy = ['STANDARD', 'PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
        try:
            prev_index = tier_hierarchy.index(self.previous_tier)
            new_index = tier_hierarchy.index(self.new_tier)
            return new_index > prev_index
        except ValueError:
            return False

    @property
    def is_downgrade(self):
        """Indique si c'est un downgrade vers un tier inférieur"""
        tier_hierarchy = ['STANDARD', 'PREMIUM_BASIC', 'PREMIUM_ADVANCED', 'PREMIUM_PRO']
        try:
            prev_index = tier_hierarchy.index(self.previous_tier)
            new_index = tier_hierarchy.index(self.new_tier)
            return new_index < prev_index
        except ValueError:
            return False

    def get_tier_change_impact(self):
        """Retourne l'impact du changement de tier"""
        from home.utils.UserTierManager import UserTierManager
        
        prev_limits = UserTierManager.get_tier_limits(self.previous_tier)
        new_limits = UserTierManager.get_tier_limits(self.new_tier)
        
        impact = {}
        for key in prev_limits.keys():
            prev_val = prev_limits[key]
            new_val = new_limits[key]
            impact[key] = {
                'previous': prev_val,
                'new': new_val,
                'change': new_val - prev_val,
                'percentage_change': ((new_val - prev_val) / prev_val * 100) if prev_val > 0 else 0
            }
        
        return impact
