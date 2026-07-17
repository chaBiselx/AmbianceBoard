from django.test import SimpleTestCase, tag

from main.domain.common.service.AsyncDownloadStrategyFactory import AsyncDownloadStrategyFactory
from main.domain.common.service.YoutubeAsyncDownloadStrategy import YoutubeAsyncDownloadStrategy


@tag('unitaire')
class AsyncDownloadStrategyFactoryTest(SimpleTestCase):

    def test_get_strategy_returns_youtube_strategy_for_youtube_source(self):
        factory = AsyncDownloadStrategyFactory()

        strategy = factory.get_strategy('youtube')

        self.assertIsInstance(strategy, YoutubeAsyncDownloadStrategy)

    def test_get_strategy_raises_for_unsupported_source(self):
        factory = AsyncDownloadStrategyFactory()

        with self.assertRaises(ValueError) as context:
            factory.get_strategy('vimeo')

        self.assertIn('Source de telechargement non supportee', str(context.exception))