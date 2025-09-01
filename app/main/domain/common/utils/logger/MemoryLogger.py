"""
Implémentation alternative du logger pour les tests ou le développement.
Cette implémentation peut être utilisée pour capturer les logs en mémoire ou les rediriger.
"""

from typing import List, Dict, Any
from .ILogger import ILogger


class MemoryLogger(ILogger):
    """
    Logger qui stocke les messages en mémoire.
    Utile pour les tests unitaires et le debugging.
    """
    
    def __init__(self, logger_name: str = 'memory'):
        """
        Initialise le logger mémoire.
        
        Args:
            logger_name (str): Nom du logger
        """
        self._logger_name = logger_name
        self._logs: List[Dict[str, Any]] = []
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau DEBUG"""
        self._add_log('DEBUG', message, args, kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau INFO"""
        self._add_log('INFO', message, args, kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau WARNING"""
        self._add_log('WARNING', message, args, kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau ERROR"""
        self._add_log('ERROR', message, args, kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log un message de niveau CRITICAL"""
        self._add_log('CRITICAL', message, args, kwargs)
    
    def exception(self, message: str, *args, exc_info: bool = True, **kwargs) -> None:
        """Log une exception avec la stack trace"""
        kwargs['exc_info'] = exc_info
        self._add_log('ERROR', message, args, kwargs)
    
    def _add_log(self, level: str, message: str, args: tuple, kwargs: dict) -> None:
        """Ajoute un log à la liste interne"""
        import datetime
        log_entry = {
            'timestamp': datetime.datetime.now(),
            'level': level,
            'message': message,
            'args': args,
            'kwargs': kwargs,
            'logger_name': self._logger_name
        }
        self._logs.append(log_entry)
    
    def get_logs(self, level: str = None) -> List[Dict[str, Any]]:
        """
        Retourne tous les logs ou ceux d'un niveau spécifique.
        
        Args:
            level (str, optional): Niveau de log à filtrer
            
        Returns:
            List[Dict[str, Any]]: Liste des logs
        """
        if level:
            return [log for log in self._logs if log['level'] == level.upper()]
        return self._logs.copy()
    
    def clear_logs(self) -> None:
        """Vide la liste des logs"""
        self._logs.clear()
    
    def count_logs(self, level: str = None) -> int:
        """
        Compte le nombre de logs.
        
        Args:
            level (str, optional): Niveau de log à compter
            
        Returns:
            int: Nombre de logs
        """
        if level:
            return len([log for log in self._logs if log['level'] == level.upper()])
        return len(self._logs)
    
    @property
    def logger_name(self) -> str:
        """Retourne le nom du logger"""
        return self._logger_name
    
    def __str__(self) -> str:
        """Représentation string du logger"""
        return f"MemoryLogger(name='{self._logger_name}', logs_count={len(self._logs)})"
