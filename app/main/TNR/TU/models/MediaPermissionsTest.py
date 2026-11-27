import os
import stat
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, override_settings, tag
from PIL import Image

from main.architecture.persistence.models.Music import Music
from main.architecture.persistence.models.Playlist import Playlist
from main.architecture.persistence.models.SoundBoard import SoundBoard
from main.domain.brokers.strategy.ReduceSizeImgStrategy import (
    PlaylistReduceSizeImgStrategy,
    SoundBoardReduceSizeImgStrategy,
)


@tag('unitaire')
class MediaPermissionsTest(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        settings_override = override_settings(MEDIA_ROOT=self.directory.name)
        settings_override.enable()
        self.addCleanup(settings_override.disable)

    def test_music_upload_is_readable(self):
        music = Music()
        music.file.save('audio.mp3', ContentFile(b'audio'), save=False)

        self.assertEqual(stat.S_IMODE(os.stat(music.file.path).st_mode), 0o644)

    def test_icon_upload_and_resize_are_readable(self):
        for model_class, strategy_class in (
            (Playlist, PlaylistReduceSizeImgStrategy),
            (SoundBoard, SoundBoardReduceSizeImgStrategy),
        ):
            with self.subTest(model=model_class.__name__):
                image_content = BytesIO()
                Image.new('RGB', (400, 300)).save(image_content, format='PNG')
                model = model_class()
                model.icon.save('icon.png', ContentFile(image_content.getvalue()), save=False)
                self.assertEqual(stat.S_IMODE(os.stat(model.icon.path).st_mode), 0o644)

                strategy_class().resize(model)

                self.assertEqual(stat.S_IMODE(os.stat(model.icon.path).st_mode), 0o644)
                with Image.open(model.icon.path) as resized:
                    self.assertEqual(resized.size, (200, 150))

    def test_icon_format_change_is_readable(self):
        for model_class, strategy_class in (
            (Playlist, PlaylistReduceSizeImgStrategy),
            (SoundBoard, SoundBoardReduceSizeImgStrategy),
        ):
            with self.subTest(model=model_class.__name__):
                image_content = BytesIO()
                Image.new('RGBA', (400, 300)).save(image_content, format='PNG')
                model = model_class()
                model.icon.save('icon.jpg', ContentFile(image_content.getvalue()), save=False)

                with patch.object(model, 'update') as update:
                    strategy_class().resize(model)

                update.assert_called_once()
                self.assertTrue(model.icon.name.endswith('.png'))
                self.assertEqual(stat.S_IMODE(os.stat(model.icon.path).st_mode), 0o644)