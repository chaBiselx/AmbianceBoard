import os
import stat
import tempfile
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import SimpleTestCase, tag

from main.domain.common.utils.AudioBitrateReducer import AudioBitrateReducer


@tag('unitaire')
class AudioBitrateReducerTest(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        storage = FileSystemStorage(location=self.directory.name)
        self.path = storage.path(storage.save('audio.mp3', ContentFile(b'audio')))
        self.reducer = AudioBitrateReducer(self.path)
        self.reducer.audio_loaded = True

    def test_uploaded_file_is_readable_without_conversion(self):
        with patch.object(self.reducer, 'get_bitrate', return_value=128), patch(
            'main.domain.common.utils.AudioBitrateReducer.subprocess.run'
        ) as run:
            self.reducer.reduce_bitrate()

        run.assert_not_called()
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o644)

    def test_converted_file_is_readable(self):
        os.chmod(self.path, 0o600)
        with patch.object(self.reducer, 'get_bitrate', return_value=192), patch(
            'main.domain.common.utils.AudioBitrateReducer.subprocess.run'
        ) as run:
            run.return_value.returncode = 0
            self.reducer.reduce_bitrate()

        run.assert_called_once()
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o644)

    def test_separate_output_is_readable(self):
        output_path = os.path.join(self.directory.name, 'output.mp3')
        with open(output_path, 'wb') as output:
            output.write(b'output')
        os.chmod(output_path, 0o600)
        with patch.object(self.reducer, 'get_bitrate', return_value=192), patch(
            'main.domain.common.utils.AudioBitrateReducer.subprocess.run'
        ) as run:
            run.return_value.returncode = 0
            self.reducer.reduce_bitrate(output_path)

        run.assert_called_once()
        self.assertEqual(stat.S_IMODE(os.stat(output_path).st_mode), 0o644)

    def test_failed_conversion_preserves_original(self):
        with patch.object(self.reducer, 'get_bitrate', return_value=192), patch(
            'main.domain.common.utils.AudioBitrateReducer.subprocess.run'
        ) as run:
            run.return_value.returncode = 1
            run.return_value.stderr = 'conversion failed'
            self.reducer.reduce_bitrate()

        with open(self.path, 'rb') as original:
            self.assertEqual(original.read(), b'audio')
        self.assertEqual(stat.S_IMODE(os.stat(self.path).st_mode), 0o644)
        self.assertEqual(os.listdir(self.directory.name), ['audio.mp3'])