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

from main.TNR.TU.utils.logger.LoggerFactoryTest import *
from main.TNR.TU.utils.logger.LokiLoggerTest import *
from main.TNR.TU.utils.logger.CompositeLoggerTest import *
from main.TNR.TU.utils.cache.CacheSystemTest import *


from main.TNR.TU.Service.FailedLoginAttemptServiceTest import *
from main.TNR.TU.Service.MusicServiceTest import *
from main.TNR.TU.Service.RandomizeTrackServiceTest import *
from main.TNR.TU.Service.RGPDServiceNotActiveTest import *
from main.TNR.TU.Service.RGPDServiceNotConfirmedTest import *
from main.TNR.TU.Service.ConfirmationUserServiceTest import *
from main.TNR.TU.Service.ReportContentServiceTest import *

from main.TNR.TU.UserParametersFactoryTest import *

#Config
from main.TNR.TU.config.PlaylistConfigTest import *
from main.TNR.TU.config.PlaylistStrategyTest import *

#MiddleWare
from main.TNR.TU.middleware.ErrorTrackingMiddlewareTest import *
from main.TNR.TU.middleware.DailySessionMiddlewareTest import *

#Repository
from main.TNR.TU.repository.TrackRepositoryTest import *

# Cron services tests (P0)
from main.TNR.TU.cron.CronServicesTest import *

# Websocket consumer tests (P0)
from main.TNR.TU.websocket.SharedSoundboardConsumerTest import *

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
from main.TNR.TI.utils.logger.LokiLoggerIntegrationTestCase import *
from main.TNR.TI.utils.logger.CompositeLoggerIntegrationTestCase import *

# Tests d'intégration des routes (1 route = 1 fichier = 1 classe)
# Routes publiques et SEO
from main.TNR.TI.routing.HomeRouteTest import *
from main.TNR.TI.routing.PricingRouteTest import *
from main.TNR.TI.routing.LegalNoticeRouteTest import *
from main.TNR.TI.routing.RobotsTxtRouteTest import *
from main.TNR.TI.routing.SitemapXmlRouteTest import *

# Routes d'authentification
from main.TNR.TI.routing.CreateAccountRouteTest import *
from main.TNR.TI.routing.LoginRouteTest import *
from main.TNR.TI.routing.LoginPostRouteTest import *
from main.TNR.TI.routing.LogoutRouteTest import *
from main.TNR.TI.routing.ResendEmailConfirmationRouteTest import *
from main.TNR.TI.routing.SendResetPasswordRouteTest import *

# Routes techniques
from main.TNR.TI.routing.TraceFrontRouteTest import *

# Routes Soundboards
from main.TNR.TI.routing.SoundboardsListRouteTest import *
from main.TNR.TI.routing.SoundboardsNewRouteTest import *

# Routes Settings
from main.TNR.TI.routing.SettingsIndexRouteTest import *
from main.TNR.TI.routing.UpdateThemeRouteTest import *
from main.TNR.TI.routing.DeleteAccountRouteTest import *

# Routes Playlists
from main.TNR.TI.routing.AddPlaylistRouteTest import *
from main.TNR.TI.routing.PlaylistsAllListRouteTest import *
from main.TNR.TI.routing.PlaylistCreateTrackStreamRouteTest import *

# Routes Streaming
from main.TNR.TI.routing.StreamMusicRouteTest import *

# Routes Publiques
from main.TNR.TI.routing.PublicIndexRouteTest import *
from main.TNR.TI.routing.PublicListingSoundboardRouteTest import *
from main.TNR.TI.routing.PublicReadSoundboardRouteTest import *
from main.TNR.TI.routing.PublicStreamMusicRouteTest import *
from main.TNR.TI.routing.ReportingContentRouteTest import *
from main.TNR.TI.routing.PublicFavoriteRouteTest import *

# Routes Modération
from main.TNR.TI.routing.ModeratorDashboardRouteTest import *
from main.TNR.TI.routing.ModeratorListingTagsRouteTest import *

# Routes Manager
from main.TNR.TI.routing.ManagerDashboardRouteTest import *

# Routes Partage (Shared)
from main.TNR.TI.routing.PublishSoundboardRouteTest import *
from main.TNR.TI.routing.SharedSoundboardRouteTest import *
from main.TNR.TI.routing.SharedStreamMusicRouteTest import *
