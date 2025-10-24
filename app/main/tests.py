from django.test import TestCase

from main.TNR.TU.auth.AuthBackendTest import *

from main.TNR.TU.signals.GroupsPermissionsSignalsTest import *

from main.TNR.TU.models.MusicModelTest import *
from main.TNR.TU.models.SoundBoardModelTest import *
from main.TNR.TU.models.PlaylistModelTest import *
from main.TNR.TU.models.UserModelTest import *


from main.TNR.TU.utils.ImageResizerTest import *
from main.TNR.TU.utils.ExtractPaginatorTest import *
from main.TNR.TU.utils.EmailSenderTest import *
from main.TNR.TU.utils.UrlsUtilsTest import *
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


