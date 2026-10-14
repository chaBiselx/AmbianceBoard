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

    def get_sections_with_playlists(self, soundboard: "SoundBoard", public=False):
        playlist_queryset = SoundboardPlaylist.objects.select_related("Playlist").order_by("order", "id")
        if public:
            playlist_queryset = playlist_queryset.filter(Playlist__tracks__isnull=False).distinct()

        return soundboard.sections.prefetch_related(
            Prefetch("playlists", queryset=playlist_queryset)
        )

    def get_sectioned_playlists(self, soundboard: "SoundBoard", public=False) -> List[tuple]:
        sections = self.get_sections_with_playlists(soundboard, public)
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

    def swap_sections(self, soundboard: "SoundBoard", section_a: int, section_b: int) -> bool:
        from django.db import transaction
        from main.architecture.persistence.models.SoundboardSection import SoundboardSection

        if section_a == section_b or section_a <= 0 or section_b <= 0:
            return False

        sections = SoundboardSection.objects.filter(
            SoundBoard=soundboard,
            section__in=(section_a, section_b),
        )
        if sections.count() != 2:
            return False

        section_a_obj = sections.get(section=section_a)
        section_b_obj = sections.get(section=section_b)

        with transaction.atomic():
            temporary_section = (
                SoundboardSection.objects.filter(SoundBoard=soundboard)
                .order_by('-section')
                .values_list('section', flat=True)
                .first()
                or 0
            ) + 1

            original_section_a = section_a_obj.section
            original_section_b = section_b_obj.section

            section_a_obj.section = temporary_section
            section_a_obj.save(update_fields=['section'])

            section_b_obj.section = original_section_a
            section_b_obj.save(update_fields=['section'])

            section_a_obj.section = original_section_b
            section_a_obj.save(update_fields=['section'])

        return True

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
