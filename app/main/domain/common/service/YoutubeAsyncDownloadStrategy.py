from main.architecture.persistence.models.AsyncDownloadJob import AsyncDownloadJob
from main.architecture.persistence.models.Music import Music
from main.domain.common.service.IAsyncDownloadStrategy import IAsyncDownloadStrategy
from main.domain.common.service.YoutubeAudioService import YoutubeAudioService


class YoutubeAsyncDownloadStrategy(IAsyncDownloadStrategy):

    source = "youtube"

    def create_music(self, job: AsyncDownloadJob) -> Music:
        service = YoutubeAudioService(user=job.user)
        return service.create_music_from_url(
            playlist=job.playlist,
            url=job.url,
            name=job.alternative_name,
        )