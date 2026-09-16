from typing import Any, Dict, Optional, List, TYPE_CHECKING
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from django.db import models
from django.db.models import F, Prefetch

if TYPE_CHECKING:
    from main.architecture.persistence.models.SoundBoard import SoundBoard


class SoundboardPlaylistRepository:

    def create(self, soundboard: "SoundBoard", playlist: Playlist, order: int, section: int = 1) -> SoundboardPlaylist:
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        section_obj = SoundboardSection.objects.filter(SoundBoard=soundboard, section=section).first()
        if section_obj is None:
            section_obj = SoundboardSection.objects.create(
                SoundBoard=soundboard,
                section=section,
                name=f"Section {section}",
                order=section,
            )

        return SoundboardPlaylist.objects.create(
            Playlist=playlist,
            order=order,
            section=section_obj,
        )

    def get(self, soundboard: "SoundBoard", playlist: Playlist) -> SoundboardPlaylist | None:
        try:
            return SoundboardPlaylist.objects.get(section__SoundBoard=soundboard, Playlist=playlist)
        except SoundboardPlaylist.DoesNotExist:
            return None

    def get_playlist_in_soundboard_by_uuid(self, soundboard: "SoundBoard", playlist_uuid: str) -> SoundboardPlaylist | None:
        try:
            return SoundboardPlaylist.objects.get(section__SoundBoard=soundboard, Playlist__uuid=playlist_uuid)
        except SoundboardPlaylist.DoesNotExist:
            return None

    def get_id(self, id) -> SoundboardPlaylist | None:
        try:
            return SoundboardPlaylist.objects.get(pk=id)
        except SoundboardPlaylist.DoesNotExist:
            return None

    def get_first(self, soundboard: "SoundBoard") -> SoundboardPlaylist | None:
        try:
            return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard).order_by('order').first()
        except SoundboardPlaylist.DoesNotExist:
            return None

    def get_last_index_by_section(self, soundboard: "SoundBoard", section: int) -> Optional[int]:
        last_entry = SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, section__section=section).order_by('-order').first()
        if last_entry:
            return last_entry.order
        return None

    def get_all(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return (
            SoundboardPlaylist.objects
            .filter(section__SoundBoard=soundboard)
            .select_related('Playlist', 'section')
            .order_by('section__section', 'order')
        )

    def get_all_playable(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return (
            SoundboardPlaylist.objects
            .filter(section__SoundBoard=soundboard, activable_by_player=True)
            .select_related('Playlist', 'section')
            .order_by('section__section', 'order')
        )

    def get_all_with_min_one_track(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return (
            SoundboardPlaylist.objects
            .filter(section__SoundBoard=soundboard, Playlist__tracks__isnull=False)
            .select_related('Playlist', 'section')
            .distinct()
            .order_by('section__section', 'order')
        )

    def get_playlist_formated(self, soundboard: "SoundBoard", public=False) -> Any:
        if public:
            list_playlist = self.get_all_with_min_one_track(soundboard)
        else:
            list_playlist = self.get_all(soundboard)
        dict_section = {}
        max_section = self.get_max_section(soundboard)
        for section in range(1, max_section + 1):
            dict_section[section] = []

        for sp in list_playlist:
            dict_section[sp.get_section()].append(sp.Playlist)

        soundboard.dict_section = dict_section
        soundboard.max_section = max_section
        return dict_section.items()

    def get_sectioned_playlists(self, soundboard: "SoundBoard", public=False) -> List[tuple]:
        playlist_queryset = SoundboardPlaylist.objects.select_related("Playlist").order_by("order", "id")
        if public:
            playlist_queryset = playlist_queryset.filter(Playlist__tracks__isnull=False).distinct()

        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        sections = SoundboardSection.objects.filter(SoundBoard=soundboard).order_by("section", "order", "id")
        sections = sections.prefetch_related(Prefetch("playlists", queryset=playlist_queryset))
        return [(section, list(section.playlists.all())) for section in sections]

    def get_soundboard_playlist_formated(self, soundboard: "SoundBoard") -> Any:
        list_playlist = self.get_all(soundboard)
        dict_section = {}
        for sp in list_playlist:
            section_number = sp.get_section()
            if section_number not in dict_section:
                dict_section[section_number] = []
            dict_section[section_number].append(sp)

        return dict_section.items()

    def get_soundboard_playlist_for_player_formated(self, soundboard: "SoundBoard") -> Any:
        list_playlist = self.get_all_playable(soundboard)
        dict_p_s = {}
        for sp in list_playlist:
            section_number = sp.get_section()
            if section_number not in dict_p_s:
                dict_p_s[section_number] = []
            dict_p_s[section_number].append(sp.Playlist)

        return dict_p_s.items()

    def get_max_section(self, soundboard: "SoundBoard") -> int:
        max_section = SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard).aggregate(models.Max('section__section'))['section__section__max']
        return max_section if max_section is not None else 1

    def get_all_by_section(self, soundboard: "SoundBoard", section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, section__section=section).order_by('order')

    def get_order_greater_or_equal(self, soundboard: "SoundBoard", order: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, order__gte=order).order_by('order')

    def get_order_greater_or_equal_by_section(self, soundboard: "SoundBoard", order: int, section: int) -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, order__gte=order, section__section=section).order_by('order')

    def shift_sections_from(self, soundboard: "SoundBoard", section: int) -> int:
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        sections = SoundboardSection.objects.filter(SoundBoard=soundboard, section__gte=section).order_by('-section')
        for item in sections:
            item.section += 1
            item.save()
        return sections.count()

    def shift_sections_down_from(self, soundboard: "SoundBoard", section: int) -> int:
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        sections = SoundboardSection.objects.filter(SoundBoard=soundboard, section__gte=section).order_by('section')
        count = 0
        for item in sections:
            item.section -= 1
            item.save()
            count += 1
        return count

    def count_sections(self, soundboard: "SoundBoard") -> int:
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        return SoundboardSection.objects.filter(SoundBoard=soundboard).count()

    def delete_section(self, soundboard: "SoundBoard", section: int) -> None:
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, section__section=section).delete()
        SoundboardSection.objects.filter(SoundBoard=soundboard, section=section).delete()

    def delete(self, soundboard: "SoundBoard", playlist: Playlist) -> tuple:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard, Playlist=playlist).delete()

    def count(self, soundboard: "SoundBoard") -> int:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard).count()

    def get_list_shortcut_keyboard(self, soundboard: "SoundBoard") -> List[SoundboardPlaylist]:
        return SoundboardPlaylist.objects.filter(section__SoundBoard=soundboard).exclude(shortcut_keyboard__isnull=True).exclude(shortcut_keyboard__exact='').order_by('section__section', 'order')

