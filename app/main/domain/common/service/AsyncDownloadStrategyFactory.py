from typing import Dict, Iterable, Optional

from main.domain.common.service.IAsyncDownloadStrategy import IAsyncDownloadStrategy
from main.domain.common.service.YoutubeAsyncDownloadStrategy import YoutubeAsyncDownloadStrategy


class AsyncDownloadStrategyFactory:

    def __init__(
        self,
        strategies: Optional[Iterable[IAsyncDownloadStrategy]] = None,
    ) -> None:
        available_strategies = strategies or [YoutubeAsyncDownloadStrategy()]
        self._strategies: Dict[str, IAsyncDownloadStrategy] = {
            strategy.source.lower(): strategy
            for strategy in available_strategies
            if strategy.source
        }

    def get_strategy(self, source: str) -> IAsyncDownloadStrategy:
        normalized_source = (source or "").strip().lower()
        strategy = self._strategies.get(normalized_source)
        if strategy is None:
            raise ValueError(f"Source de telechargement non supportee: {source}")
        return strategy