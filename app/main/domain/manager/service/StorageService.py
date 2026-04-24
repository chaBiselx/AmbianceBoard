import os
import shutil
from django.conf import settings


class StorageService:
    @staticmethod
    def get_dir_size(path: str) -> int:
        total = 0
        if os.path.exists(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total += os.path.getsize(fp)
        return total
    
    @staticmethod    
    def get_file_count(path: str) -> int:
        count = 0
        if os.path.exists(path):
            for dirpath, dirnames, filenames in os.walk(path):
                count += len(filenames)
        return count
    
    @staticmethod
    def get_storage_usage() -> dict:
        """
        Calcule l'espace de stockage utilisé par les fichiers média.
        Retourne un dictionnaire avec la taille totale et par sous-dossier.
        """
        media_root = settings.MEDIA_ROOT

        subdirs = ['musics', 'playlistIcon', 'soundBoardIcon']
        details = []
        total_size = 0

        for subdir in subdirs:
            path = os.path.join(media_root, subdir)
            size = StorageService.get_dir_size(path)
            count = StorageService.get_file_count(path)
            total_size += size
            details.append({
                'name': subdir,
                'size': size,
                'size_formatted': StorageService._format_size(size),
                'file_count': count,
            })

        project_root = settings.BASE_DIR
        project_size = StorageService.get_dir_size(str(project_root)) - total_size
        project_file_count = StorageService.get_file_count(str(project_root)) - sum(d['file_count'] for d in details)

        disk = shutil.disk_usage(str(media_root))

        return {
            'total_size': total_size,
            'total_size_formatted': StorageService._format_size(total_size),
            'details': details,
            'project_size': project_size,
            'project_size_formatted': StorageService._format_size(project_size),
            'project_file_count': project_file_count,
            'disk_total': disk.total,
            'disk_total_formatted': StorageService._format_size(disk.total),
            'disk_used': disk.used,
            'disk_used_formatted': StorageService._format_size(disk.used),
            'disk_free': disk.free,
            'disk_free_formatted': StorageService._format_size(disk.free),
            'disk_used_percent': round(disk.used / disk.total * 100, 1) if disk.total > 0 else 0,
        }

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 o"
        units = ['o', 'Ko', 'Mo', 'Go', 'To']
        i = 0
        size = float(size_bytes)
        while size >= 1024 and i < len(units) - 1:
            size /= 1024
            i += 1
        return f"{size:.2f} {units[i]}"
