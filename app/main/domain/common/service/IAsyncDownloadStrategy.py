from abc import ABC, abstractmethod

from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
from main.architecture.persistence.models.Music import Music


class IAsyncDownloadStrategy(ABC):

    source = ""

    @abstractmethod
    def create_music(self, job: AsyncDownloadJob) -> Music:
        raise NotImplementedError