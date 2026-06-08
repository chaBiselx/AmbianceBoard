import os


class SystemLoadService:
    """
    Service pour évaluer la charge système courante.
    """

    @staticmethod
    def is_loaded(threshold: float) -> bool:
        """
        Vérifie si le système est chargé en se basant sur le load average 1 min.
        Retourne True si la charge normalisée (load / nb_cpus) dépasse le seuil.
        """
        try:
            load_1min = os.getloadavg()[0]
            cpu_count = os.cpu_count() or 1
            normalized_load = load_1min / cpu_count
            return normalized_load > threshold
        except (OSError, AttributeError):
            return False
