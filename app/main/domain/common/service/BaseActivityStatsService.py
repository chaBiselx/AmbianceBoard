"""
Service de base pour les statistiques d'activité.

Ce service fournit des méthodes communes pour analyser les données d'activité
et générer des statistiques d'usage de l'application.
"""

from typing import Dict, List
from datetime import datetime


class BaseActivityStatsService:
    """
    Service de base pour analyser les statistiques d'activité.
    
    Fournit des méthodes communes pour la génération de données statistiques
    basées sur les données de traçage d'activité.
    """
    
    def _generated_line_graph_data(self, start_date: datetime, end_date: datetime, activity_data: List[Dict], transposition_titles: Dict|None = None) -> dict:
        """
        Génère des données statistiques formatées à partir des données d'activité brutes.
        
        Args:
            start_date: Date de début de la période
            end_date: Date de fin de la période
            activity_data: Données d'activité brutes groupées par type et date
            
        Returns:
            Dictionnaire contenant les données formatées par type d'activité
        """
        # Organisation des données par type d'activité
        data_by_type = {}
        for item in activity_data:
            activity_type = item['activity_type']
            date = item['date'].strftime('%Y-%m-%d') if item['date'] else None
            count = item['count']
            
            if activity_type not in data_by_type:
                data_by_type[activity_type] = []
            
            data_by_type[activity_type].append({
                'date': date,
                'count': count
            })

        # Conversion en format de sortie structuré
        result_data = {}
        for activity_type, daily_counts in data_by_type.items():
            label = transposition_titles.get(activity_type, activity_type) if transposition_titles else activity_type
            result_data[activity_type] = {
                'key': activity_type,
                'label': label,
                'data': daily_counts
            }

        return {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'data': result_data
        }
