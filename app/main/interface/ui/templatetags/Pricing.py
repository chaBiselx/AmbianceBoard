from django import template
from decimal import Decimal, ROUND_HALF_UP
from main.application.helper.PricingHelper import PricingHelper

register = template.Library()

@register.filter
def ht_to_ttc(price_ht):
    """
    Formate un prix HT en affichage TTC avec devise.
    
    Args:
        price_ht: Le prix hors taxe
        currency: La devise à afficher (par défaut 'EUR')
        
    Returns:
        str: Le prix formaté avec TTC
    """
    return PricingHelper.ht_to_ttc(price_ht)

@register.filter
def format_price_ttc(price_ht, currency='EUR'):
    """
    Formate un prix HT en affichage TTC avec devise.
    
    Args:
        price_ht: Le prix hors taxe
        currency: La devise à afficher (par défaut 'EUR')
        
    Returns:
        str: Le prix formaté avec TTC
    """
    return PricingHelper.format_price_ttc(price_ht, currency)


@register.simple_tag
def get_tva_rate():
    """
    Retourne le taux de TVA configuré.
    
    Returns:
        Decimal: Le taux de TVA en pourcentage
    """
    return PricingHelper.get_tva_rate()

@register.simple_tag
def get_currency_symbol(devise: str = None):
    """
    Retourne le symbole de la devise configurée.
    
    Returns:
        str: Le symbole de la devise (par défaut '€')
    """
    return PricingHelper.get_currency_symbol(devise)


