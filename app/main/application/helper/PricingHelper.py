from main.domain.common.utils.settings import Settings
from main.domain.common.enum.DeviseEnum import DeviseEnum
from decimal import Decimal, ROUND_HALF_UP


class PricingHelper:
    
    @staticmethod
    def ht_to_ttc(price_ht, currency='EUR'):
        """
        Convertit un prix HT en TTC en appliquant la TVA configurée.
        
        Args:
            price_ht: Le prix hors taxe (peut être int, float, str ou Decimal)
            
        Returns:
            Decimal: Le prix TTC arrondi à 2 décimales
        """
        if price_ht is None:
            return None
        
        try:
            from decimal import Decimal, ROUND_HALF_UP
            
            # Convertir en Decimal pour une précision optimale
            if isinstance(price_ht, str):
                price_ht = Decimal(price_ht)
            elif isinstance(price_ht, (int, float)):
                price_ht = Decimal(str(price_ht))
            elif not isinstance(price_ht, Decimal):
                price_ht = Decimal(str(price_ht))
                
            price_ht = PricingHelper.conversion(price_ht, 'EUR', currency)
            
            # Récupérer le taux de TVA depuis les settings
            tva_rate = PricingHelper.get_tva_rate()

            # Calculer le prix TTC
            price_ttc = price_ht * (1 + tva_rate / 100)
            
            # Arrondir à 2 décimales
            return price_ttc.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except (ValueError, TypeError):
            return price_ht

    @staticmethod
    def format_price_ttc(price_ht, currency='EUR'):
        """
        Formate un prix HT en affichage TTC avec devise.
        
        Args:
            price_ht: Le prix hors taxe
            currency: La devise à afficher (par défaut 'EUR')
            
        Returns:
            str: Le prix formaté avec TTC
        """
        if price_ht is None:
            return "Gratuit"
        
        currency_symbol = PricingHelper.get_currency_symbol(currency)
        
        try:
            price_ttc = PricingHelper.ht_to_ttc(price_ht)
            if price_ttc is None:
                return "Gratuit"
            
            # Formater le prix avec 2 décimales si nécessaire
            if price_ttc % 1 == 0:
                # Prix entier, pas de décimales
                return f"{int(price_ttc)}{currency_symbol} TTC"
            else:
                # Prix avec décimales
                return f"{price_ttc:.2f}{currency_symbol} TTC"
                
        except (ValueError, TypeError):
            return str(price_ht)
    
    @staticmethod
    def get_tva_rate():
        """
        Retourne le taux de TVA configuré.
        
        Returns:
            Decimal: Le taux de TVA en pourcentage
        """
        return Decimal(str(Settings.get('APP_TVA', 20.0)))
    
    @staticmethod
    def get_currency_symbol(devise: str = None):
        """
        Retourne le symbole de la devise configurée.
        
        Returns:
            str: Le symbole de la devise 
        """
        if devise:
            return DeviseEnum.search(devise).value
        return PricingHelper.get_default_currency()

    @staticmethod
    def get_default_currency():
        """
        Retourne la devise configurée.
        
        Returns:
            str: La devise (par défaut 'EUR')
        """
        return DeviseEnum.search(Settings.get('APP_CURRENCY', 'EUR')).value

    @staticmethod
    def conversion(price, from_devise: str, to_devise: str):
        """
        Convertit un prix d'une devise à une autre.
        
        Args:
            price: Le prix à convertir
            from_devise: La devise d'origine
            to_devise: La devise de destination
            
        Returns:
            Decimal: Le prix converti
        """
        # Pour l'instant, on ne gère qu'une seule devise (EUR)
        return price