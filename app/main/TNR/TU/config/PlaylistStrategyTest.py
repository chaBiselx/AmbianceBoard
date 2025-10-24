import unittest
from main.domain.common.strategy.playlistConfig.ConfigInstant import ConfigInstant
from main.domain.common.strategy.playlistConfig.ConfigMusic import ConfigMusic
from main.domain.common.strategy.playlistConfig.ConfigAmbient import ConfigAmbient
from main.domain.common.strategy.PlaylistStrategy import PlaylistStrategy
from main.domain.common.enum.PlaylistTypeEnum import PlaylistTypeEnum


class PlaylistStrategyTest(unittest.TestCase):
    """Tests pour les configurations de playlist - vérification structure"""

    def test_config_instant(self):
        """Test que ConfigInstant a une structure cohérente"""
        config = ConfigInstant()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))

    def test_config_music(self):
        """Test que ConfigMusic a une structure cohérente"""
        config = ConfigMusic()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))

    def test_config_ambient(self):
        """Test que ConfigAmbient a une structure cohérente"""
        config = ConfigAmbient()
        self.assertEqual(set(config.default_data.keys()), set(config.structure_data.keys()))


class PlaylistStrategyTest(unittest.TestCase):
    """Tests pour PlaylistStrategy - sélection de stratégie selon type"""

    def setUp(self):
        """Configuration initiale des tests"""
        self.strategy_factory = PlaylistStrategy()

    def test_get_strategy_instant(self):
        """Test sélection de la stratégie Instant"""
        strategy = self.strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name)
        
        self.assertIsInstance(strategy, ConfigInstant)
        self.assertIsNotNone(strategy.default_data)
        self.assertIsNotNone(strategy.structure_data)

    def test_get_strategy_ambient(self):
        """Test sélection de la stratégie Ambient"""
        strategy = self.strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name)
        
        self.assertIsInstance(strategy, ConfigAmbient)
        self.assertIsNotNone(strategy.default_data)
        self.assertIsNotNone(strategy.structure_data)

    def test_get_strategy_music(self):
        """Test sélection de la stratégie Music"""
        strategy = self.strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        
        self.assertIsInstance(strategy, ConfigMusic)
        self.assertIsNotNone(strategy.default_data)
        self.assertIsNotNone(strategy.structure_data)

    def test_get_strategy_fallback_to_instant(self):
        """Test que la stratégie par défaut est ConfigInstant pour type inconnu"""
        strategy = self.strategy_factory.get_strategy('UNKNOWN_TYPE')
        
        self.assertIsInstance(strategy, ConfigInstant)

    def test_get_strategy_empty_string_fallback(self):
        """Test fallback avec chaîne vide"""
        strategy = self.strategy_factory.get_strategy('')
        
        self.assertIsInstance(strategy, ConfigInstant)

    def test_get_strategy_none_fallback(self):
        """Test fallback avec None"""
        strategy = self.strategy_factory.get_strategy(None)
        
        self.assertIsInstance(strategy, ConfigInstant)

    def test_get_strategy_case_sensitive(self):
        """Test que la sélection est sensible à la casse"""
        # Les enums sont en majuscules, donc minuscules devrait fallback
        strategy = self.strategy_factory.get_strategy('playlist_type_music')
        
        self.assertIsInstance(strategy, ConfigInstant)

    def test_strategies_are_singleton(self):
        """Test que les stratégies sont réutilisées (pattern Singleton)"""
        strategy1 = self.strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        strategy2 = self.strategy_factory.get_strategy(PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name)
        
        # Devrait être la même instance (optimisation mémoire)
        self.assertIs(strategy1, strategy2)

    def test_all_strategies_available(self):
        """Test que toutes les stratégies attendues sont disponibles"""
        expected_types = [
            PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name,
            PlaylistTypeEnum.PLAYLIST_TYPE_AMBIENT.name,
            PlaylistTypeEnum.PLAYLIST_TYPE_MUSIC.name
        ]
        
        for playlist_type in expected_types:
            strategy = self.strategy_factory.get_strategy(playlist_type)
            self.assertIsNotNone(strategy)
            # Vérifier que ce n'est pas toujours ConfigInstant (sauf pour INSTANT)
            if playlist_type != PlaylistTypeEnum.PLAYLIST_TYPE_INSTANT.name:
                self.assertNotEqual(type(strategy).__name__, 'ConfigInstant',
                                  f"Type {playlist_type} ne devrait pas retourner ConfigInstant")


if __name__ == '__main__':
    unittest.main()
