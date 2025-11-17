"""
Énumération des périodes disponibles pour les graphiques du tableau de bord.

Définit les différentes périodes de temps sélectionnables pour l'affichage
des données statistiques dans les graphiques du manager.
"""

from main.domain.common.enum.BaseEnum import BaseEnum


class ChartPeriodEnum(BaseEnum):
    """
    Énumération des périodes de temps pour les graphiques.
    
    Chaque membre contient:
    - name: Le nombre de jours (utilisé comme clé)
    - value: Le label affiché à l'utilisateur
    """
    
    WEEK_1 = "1 semaine"
    WEEK_2 = "2 semaines"
    MONTH_1 = "1 mois"
    MONTH_2 = "2 mois"
    MONTH_3 = "3 mois"
    MONTH_6 = "6 mois"
    YEAR_1 = "1 an"
    
    @classmethod
    def get_days_mapping(cls):
        """
        Retourne un dictionnaire mappant les jours aux labels de période.
        
        Returns:
            Dict[str, str]: Dictionnaire avec les jours comme clés et les labels comme valeurs
        """
        return {
            "7": cls.WEEK_1.value,
            "14": cls.WEEK_2.value,
            "31": cls.MONTH_1.value,
            "61": cls.MONTH_2.value,
            "91": cls.MONTH_3.value,
            "183": cls.MONTH_6.value,
            "365": cls.YEAR_1.value,
        }
    
    @classmethod
    def is_valid_period(cls, period: str) -> bool:
        """
        Vérifie si une période (en jours) est valide.
        
        Args:
            period: Le nombre de jours sous forme de chaîne
            
        Returns:
            bool: True si la période est valide, False sinon
        """
        return period in cls.get_days_mapping()
    
    @classmethod
    def get_default_period(cls) -> str:
        """
        Retourne la période par défaut.
        
        Returns:
            str: La période par défaut (91 jours = 3 mois)
        """
        return "91"
