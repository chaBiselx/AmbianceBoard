from typing import Any, Optional, List
from main.architecture.persistence.models.LinkMusic import LinkMusic



class LinkMusicRepository:

    def get_link(self, id_link:int) -> LinkMusic|None:
        try:
            return LinkMusic.objects.get(id=id_link)
        except LinkMusic.DoesNotExist:
            return None

   