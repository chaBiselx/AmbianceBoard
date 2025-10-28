from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from main.domain.common.enum.PermissionEnum import PermissionEnum
from main.domain.manager.decorator.cron_decorator import cron_view
from main.domain.cron.service.MediaAudioService import MediaAudioService
from main.domain.cron.service.MediaImgPlaylistService import MediaImgPlaylistService
from main.domain.cron.service.MediaImgSoundboardService import MediaImgSoundboardService
from main.domain.cron.service.UserTierExpirationService  import UserTierExpirationService
from main.domain.cron.service.DomainBlacklistCronService import DomainBlacklistCronService
from main.domain.cron.service.SharedSoundboardService import SharedSoundboardService
from main.domain.cron.service.PurgeUserActivityService import PurgeUserActivityService


@login_required
@require_http_methods(['GET'])
@permission_required('auth.' + PermissionEnum.MANAGER_EXECUTE_BATCHS.name, login_url='login')
def listing_cron_views(request):
    """
    Render the manager cron views page.
    """
    return render(request, 'Html/Manager/cron_listing.html')


@cron_view("ClearMediaFolder")
def clean_media_folder(request) -> JsonResponse:
    MediaAudioService().clear_media_audio()
    MediaImgPlaylistService().clear_media_img()
    MediaImgSoundboardService().clear_media_img()


@cron_view("ExpireAccount")
def expire_account(request) -> JsonResponse:
    user_tier_expiration_service = UserTierExpirationService()
    user_tier_expiration_service.handle_expired_tiers()
    user_tier_expiration_service.send_expiration_warnings()


@cron_view("SyncDomainBlacklist")
def sync_domain_blacklist(request) -> JsonResponse:
    domain_blacklist_cron_service = DomainBlacklistCronService()
    domain_blacklist_cron_service.sync_blacklist()


@cron_view("PurgeExpiredSharedSoundboard")
def purge_expired_shared_soundboard(request) -> JsonResponse:
    SharedSoundboardService().purge_expired_shared_soundboard()


@cron_view("PurgeOldUserActivity")
def purge_old_user_activity(request) -> JsonResponse:
    PurgeUserActivityService().purge()
