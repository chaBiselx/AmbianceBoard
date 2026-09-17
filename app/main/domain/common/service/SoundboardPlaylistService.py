from django.db import transaction
from main.architecture.persistence.models.SoundboardPlaylist import SoundboardPlaylist
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.architecture.persistence.models.SoundboardSection import SoundboardSection
from main.architecture.persistence.repository.SoundboardPlaylistRepository import SoundboardPlaylistRepository


class SoundboardPlaylistService:

    def __init__(self, soundboard: SoundBoard):
        self.soundboard = soundboard
        self.soundboard_playlist_repository = SoundboardPlaylistRepository()

    def _get_or_create_section(self, section: int) -> SoundboardSection:
        section_obj = SoundboardSection.objects.filter(SoundBoard=self.soundboard, section=section).first()
        if section_obj is None:
            section_obj = SoundboardSection.objects.create(
                SoundBoard=self.soundboard,
                section=section,
                name=f"Section {section}",
                order=section,
            )
        return section_obj

    def add_default(self, playlist: Playlist, section: int = 1):
        last_index_bdd = self.soundboard_playlist_repository.get_last_index_by_section(self.soundboard, section)
        last_index = last_index_bdd + 1 if last_index_bdd is not None else 1
        order = self.__check_order(last_index)
        self.soundboard_playlist_repository.create(self.soundboard, playlist, order, section)
        return self

    def add(self, playlist: Playlist, order: int | None = None, section: int = 1):
        if self.soundboard_playlist_repository.get(self.soundboard, playlist) is not None:
            return self

        order = self.__check_order(order)

        if order is not None:
            self.reorder_from(order, section)

        self.soundboard_playlist_repository.create(self.soundboard, playlist, order, section)
        return self

    def update(self, playlist: Playlist, order: int | None = None, section: int = 1):
        soundboard_playlist = self.soundboard_playlist_repository.get(self.soundboard, playlist)
        if soundboard_playlist is None:
            return self

        previous_section = soundboard_playlist.get_section()

        order = self.__check_order(order)

        if order is not None:
            self.reorder_from(order, section)

        soundboard_playlist.order = order
        soundboard_playlist.section = self._get_or_create_section(section)
        soundboard_playlist.save()
        self.reorder_section(section)
        if previous_section != section:
            self.reorder_section(previous_section)

        return self

    def __check_order(self, order: int | None = None):
        if order is not None and order <= 0:
            order = None
        if order is None:
            order = self._new_order()
        return order

    def remove(self, playlist: Playlist, section: int = 1):
        self.soundboard_playlist_repository.delete(self.soundboard, playlist)
        self.reorder_section(section)
        return self

    def _new_order(self):
        if self.soundboard_playlist_repository.count(self.soundboard) == 0:
            return 1
        else:
            return self.soundboard_playlist_repository.get_first(self.soundboard).order + 1

    def reorder_section(self, section=1):
        soundboard_playlists = self.soundboard_playlist_repository.get_all_by_section(self.soundboard, section)
        new_order = 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self

    def reorder_from(self, order, section=1):
        soundboard_playlists = self.soundboard_playlist_repository.get_order_greater_or_equal_by_section(self.soundboard, order, section)
        new_order = order + 1
        for soundboard_playlist in soundboard_playlists:
            soundboard_playlist.order = new_order
            soundboard_playlist.save()
            new_order += 1
        return self

    @transaction.atomic
    def insert_section(self, section: int):
        if section <= 0:
            return self

        self.soundboard_playlist_repository.shift_sections_from(self.soundboard, section)
        self._get_or_create_section(section)
        return self

    @transaction.atomic
    def rename_section(self, section: int, name: str):
        if section <= 0:
            return self

        section_obj = self._get_or_create_section(section)
        section_obj.name = (name or "").strip()[:255]
        section_obj.save()
        return self

    @transaction.atomic
    def delete_section(self, section: int):
        if section <= 0:
            return self
        if self.soundboard_playlist_repository.count_sections(self.soundboard) <= 1:
            return self

        self.soundboard_playlist_repository.delete_section(self.soundboard, section)
        self.soundboard_playlist_repository.shift_sections_down_from(self.soundboard, section)
        return self
