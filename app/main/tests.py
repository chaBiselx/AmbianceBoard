from django.test import TestCase

# =======================================================================
# ======================== TEST UNITAIRE ================================
# =======================================================================
from main.TNR.TU.auth.AuthBackendTest import *

from main.TNR.TU.signals.GroupsPermissionsSignalsTest import *

from main.TNR.TU.models.MusicModelTest import *
from main.TNR.TU.models.SoundBoardModelTest import *
from main.TNR.TU.models.PlaylistModelTest import *
from main.TNR.TU.models.UserModelTest import *


from main.TNR.TU.utils.ImageResizerTest import *
from main.TNR.TU.utils.ExtractPaginatorTest import *
from main.TNR.TU.utils.EmailSenderTest import *
from main.TNR.TU.utils.SettingsTest import *
from main.TNR.TU.utils.SoundBoardTemplateTagTest import *
from main.TNR.TU.utils.logger.GraylogLoggerTest import *

from main.TNR.TU.utils.logger.LoggerFactoryTest import *
from main.TNR.TU.utils.logger.CompositeLoggerTest import *
from main.TNR.TU.utils.cache.CacheSystemTest import *
from main.TNR.TU.utils.cache.RedisCacheSystemTest import *


from main.TNR.TU.Service.FailedLoginAttemptServiceTest import *
from main.TNR.TU.Service.MusicServiceTest import *
from main.TNR.TU.Service.RandomizeTrackServiceTest import *
from main.TNR.TU.Service.RGPDServiceNotActiveTest import *
from main.TNR.TU.Service.RGPDServiceNotConfirmedTest import *
from main.TNR.TU.Service.ConfirmationUserServiceTest import *
from main.TNR.TU.Service.ReportContentServiceTest import *
from main.TNR.TU.Service.PlaylistDuplicationServiceTest import *
from main.TNR.TU.Service.PlaylistProposalServiceTest import *
from main.TNR.TU.Service.PlaylistDataServiceTest import *
from main.TNR.TU.Service.DefaultColorPlaylistServiceTest import *
from main.TNR.TU.Service.SoundboardPlaylistServiceTest import *
from main.TNR.TU.Service.SoundboardScriptServiceTest import *

from main.TNR.TU.UserParametersFactoryTest import *
from main.TNR.TU.UserTierManagerTest import *

#Config
from main.TNR.TU.config.PlaylistConfigTest import *
from main.TNR.TU.config.PlaylistStrategyTest import *

#MiddleWare
from main.TNR.TU.middleware.ErrorTrackingMiddlewareTest import *
from main.TNR.TU.middleware.DailySessionMiddlewareTest import *
from main.TNR.TU.middleware.PublicVisitTrackingMiddlewareTest import *

#Repository
from main.TNR.TU.repository.AsyncDownloadJobRepositoryTest import *
from main.TNR.TU.repository.DomainBlacklistRepositoryTest import *
from main.TNR.TU.repository.FailedLoginAttemptRepositoryTest import *
from main.TNR.TU.repository.GeneralNotificationRepositoryTest import *
from main.TNR.TU.repository.LinkMusicRepositoryTest import *
from main.TNR.TU.repository.MusicRepositoryTest import *
from main.TNR.TU.repository.PlaylistColorUserRepositoryTest import *
from main.TNR.TU.repository.PlaylistDuplicationHistoryRepositoryTest import *
from main.TNR.TU.repository.PlaylistTagRepositoryTest import *
from main.TNR.TU.repository.PlaylistRepositoryTest import *
from main.TNR.TU.repository.RepositoryFiltersTest import *
from main.TNR.TU.repository.SoundBoardRepositoryTest import *
from main.TNR.TU.repository.TrackRepositoryTest import *
from main.TNR.TU.repository.SoundboardPlaylistRepositoryTest import * 
from main.TNR.TU.repository.TagRepositoryTest import *
from main.TNR.TU.repository.TestUserRepository import *
from main.TNR.TU.repository.TrafficAttributionVisitRepositoryTest import *
from main.TNR.TU.repository.UserModerationLogRepositoryTest import *
from main.TNR.TU.repository.UserNotificationDismissalRepositoryTest import *
from main.TNR.TU.repository.UserPreferenceRepositoryTest import *
#form 
from main.TNR.TU.forms.manager.ManagerEmailValidationUtilsTest import *
from main.TNR.TU.forms.private.PlaylistFormTest import *

# Cron services tests (P0)
from main.TNR.TU.cron.CronServicesTest import *



# Reporting & Moderation tests (P0)
from main.TNR.TU.reporting.ReportingModerationTest import *

# Helper
from main.TNR.TU.helper.PricingHelperTest import *

# mailing
from main.TNR.TU.email.EmailSenderTest import *
from main.TNR.TU.email.ModeratorAndUserEmailTest import *

# =======================================================================
# ======================== TEST INTEGRATION =============================
# =======================================================================
from main.TNR.TI.utils.UrlsUtilsTest import *

from main.TNR.TI.utils.logger.LoggerFactoryIntegrationTestCase import *
from main.TNR.TI.utils.logger.CompositeLoggerIntegrationTestCase import *

# Tests d'intégration des routes (1 route = 1 fichier = 1 classe)
# Routes publiques et SEO
from main.TNR.TI.routing.HomeRouteTest import *
from main.TNR.TI.routing.PricingRouteTest import *
from main.TNR.TI.routing.LegalNoticeRouteTest import *
from main.TNR.TI.routing.SupportContactRouteTest import *
from main.TNR.TI.routing.RobotsTxtRouteTest import *
from main.TNR.TI.routing.SitemapXmlRouteTest import *
from main.TNR.TI.routing.FaqRouteTest import *
from main.TNR.TI.routing.LlmsTxtRouteTest import *

# Routes d'authentification
from main.TNR.TI.routing.CreateAccountRouteTest import *
from main.TNR.TI.routing.LoginRouteTest import *
from main.TNR.TI.routing.LoginPostRouteTest import *
from main.TNR.TI.routing.LogoutRouteTest import *
from main.TNR.TI.routing.ResendEmailConfirmationRouteTest import *
from main.TNR.TI.routing.SendResetPasswordRouteTest import *
from main.TNR.TI.routing.CallbackOauthGoogleRouteTest import *
from main.TNR.TI.routing.ConfirmAccountRouteTest import *
from main.TNR.TI.routing.TokenValidationResetPasswordRouteTest import *

# Routes techniques
from main.TNR.TI.routing.TraceFrontRouteTest import *
from main.TNR.TI.routing.SetLanguageRouteTest import *
from main.TNR.TI.routing.OnboardingContextRouteTest import *
from main.TNR.TI.routing.DismissGeneralNotificationRouteTest import *
from main.TNR.TI.routing.DismissTraceUserActivityRouteTest import *

# Routes Soundboards
from main.TNR.TI.routing.SoundboardsListRouteTest import *
from main.TNR.TI.routing.SoundboardsNewRouteTest import *
from main.TNR.TI.routing.SoundboardsReadRouteTest import *
from main.TNR.TI.routing.OrganizeSoundboardUpdateRouteTest import *
from main.TNR.TI.routing.SoundboardEditModeDuplicatePlaylistRouteTest import *
from main.TNR.TI.routing.SoundboardEditModeMyPlaylistRouteTest import *
from main.TNR.TI.routing.SoundboardScriptRouteTest import *
from main.TNR.TI.routing.PlaylistProposalRouteTest import *
from main.TNR.TI.routing.OrganizeSoundboardRouteTest import *
from main.TNR.TI.routing.SoundboardEditModePanelRouteTest import *
from main.TNR.TI.routing.SoundboardEditModePlaylistListRouteTest import *
from main.TNR.TI.routing.SoundboardEditModeCreatePlaylistRouteTest import *
from main.TNR.TI.routing.SoundboardsUpdateRouteTest import *
from main.TNR.TI.routing.SoundboardsDeleteRouteTest import *
from main.TNR.TI.routing.ListSoundboardPlaylistsSpecificRouteTest import *
from main.TNR.TI.routing.UpdateActionablePlaylistsForPlayersRouteTest import *
from main.TNR.TI.routing.UpdateShortcutPlaylistsForPlayersRouteTest import *
from main.TNR.TI.routing.AddMusicFromSoundboardRouteTest import *
from main.TNR.TI.routing.PlaylistProposalsListRouteTest import *
from main.TNR.TI.routing.PlaylistProposalTrackStreamRouteTest import *

# Routes Settings
from main.TNR.TI.routing.SettingsIndexRouteTest import *
from main.TNR.TI.routing.UpdateThemeRouteTest import *
from main.TNR.TI.routing.DeleteAccountRouteTest import *
from main.TNR.TI.routing.UpdateDimensionsRouteTest import *
from main.TNR.TI.routing.DefaultPlaylistTypeRouteTest import *
from main.TNR.TI.routing.UpdatePlaylistDimRouteTest import *
from main.TNR.TI.routing.UpdateSoundboardDimRouteTest import *

# Routes Playlists
from main.TNR.TI.routing.AddPlaylistRouteTest import *
from main.TNR.TI.routing.PlaylistsAllListRouteTest import *
from main.TNR.TI.routing.PlaylistCreateTrackStreamRouteTest import *
from main.TNR.TI.routing.AsyncDownloadJobsRecentRouteTest import *
from main.TNR.TI.routing.PlaylistsAllCopiableListRouteTest import *
from main.TNR.TI.routing.PlaylistPreviewRouteTest import *
from main.TNR.TI.routing.PlaylistDuplicateRouteTest import *
from main.TNR.TI.routing.PlaylistUpdateRouteTest import *
from main.TNR.TI.routing.PlaylistDeleteRouteTest import *
from main.TNR.TI.routing.PlaylistDescribeTypeRouteTest import *

# Routes Musiques / Liens
from main.TNR.TI.routing.AddMusicRouteTest import *
from main.TNR.TI.routing.UploadMultipleMusicRouteTest import *
from main.TNR.TI.routing.EditMusicRouteTest import *
from main.TNR.TI.routing.DeleteMusicRouteTest import *
from main.TNR.TI.routing.AddLinkRouteTest import *
from main.TNR.TI.routing.AddLinkAjaxRouteTest import *
from main.TNR.TI.routing.EditLinkRouteTest import *
from main.TNR.TI.routing.DeleteLinkRouteTest import *

# Routes Streaming
from main.TNR.TI.routing.StreamMusicRouteTest import *

# Routes Publiques
from main.TNR.TI.routing.PublicIndexRouteTest import *
from main.TNR.TI.routing.PublicListingSoundboardRouteTest import *
from main.TNR.TI.routing.PublicReadSoundboardRouteTest import *
from main.TNR.TI.routing.PublicStreamMusicRouteTest import *
from main.TNR.TI.routing.ReportingContentRouteTest import *
from main.TNR.TI.routing.PublicFavoriteRouteTest import *
from main.TNR.TI.routing.PublicSoundboardTracksListRouteTest import *
from main.TNR.TI.routing.PublicSpecificTrackStreamRouteTest import *
from main.TNR.TI.routing.PublicSoundboardProposeMyPlaylistListRouteTest import *
from main.TNR.TI.routing.PublicSoundboardDismissProposalRouteTest import *
from main.TNR.TI.routing.PublicProposalStreamMusicRouteTest import *
from main.TNR.TI.routing.PublicFavoriteSoundboardRouteTest import *

# Routes Statistiques publiques
from main.TNR.TI.routing.ListPublicUserSoundboardsStatsRouteTest import *
from main.TNR.TI.routing.PublicUserSoundboardsStatsRouteTest import *
from main.TNR.TI.routing.PublicUserSoundboardsFrequentationStatsRouteTest import *
from main.TNR.TI.routing.PublicUserSoundboardsAverageSessionDurationStatsRouteTest import *

# Routes Modération
from main.TNR.TI.routing.ModeratorDashboardRouteTest import *
from main.TNR.TI.routing.ModeratorListingSoundboardRouteTest import *
from main.TNR.TI.routing.ModeratorListingTagsRouteTest import *
from main.TNR.TI.routing.ModeratorListingPlaylistTagsRouteTest import *

# Routes Manager
from main.TNR.TI.routing.ManagerDashboardRouteTest import *
from main.TNR.TI.routing.ManagerActivityDashboardsRouteTest import *
from main.TNR.TI.routing.ManagerCronViewsRouteTest import *
from main.TNR.TI.routing.ManagerNotificationsRouteTest import *
from main.TNR.TI.routing.ManagerSendEmailRouteTest import *
from main.TNR.TI.routing.ManagerHomeDemoRouteTest import *
from main.TNR.TI.routing.ManagerMusicLabelerRouteTest import *
from main.TNR.TI.routing.ManagerUserTierRouteTest import *

# Routes Partage (Shared)
from main.TNR.TI.routing.PublishSoundboardRouteTest import *
from main.TNR.TI.routing.SharedSoundboardRouteTest import *
from main.TNR.TI.routing.SharedStreamMusicRouteTest import *
from main.TNR.TI.routing.SharedSoundboardRefreshRouteTest import *
from main.TNR.TI.routing.SharedProposalStreamMusicRouteTest import *

# Websocket consumer tests (P0)
from main.TNR.TI.websocket.SharedSoundboardConsumerTest import *

# =======================================================================
# ======================== STRESS TEST =============================
# =======================================================================

