import unittest
from main.domain.common.strategy.playlistConfig.ConfigInstant import ConfigInstant
from main.domain.common.strategy.playlistConfig.ConfigMusic import  ConfigMusic
from main.domain.common.strategy.playlistConfig.ConfigAmbient import ConfigAmbient

class PlaylistConfigTest(unittest.TestCase):

    def test_config_instant(self):
        config = ConfigInstant()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))

    def test_config_music(self):
        config = ConfigMusic()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))

    def test_config_ambient(self):
        config = ConfigAmbient()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))

if __name__ == '__main__':
    unittest.main()