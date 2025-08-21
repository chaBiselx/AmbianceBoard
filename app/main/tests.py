from django.test import TestCase

from main.TNR.TU.models.MusicModelTest import *
from main.TNR.TU.models.SoundBoardModelTest import *
from main.TNR.TU.models.PlaylistModelTest import *
from main.TNR.TU.models.UserModelTest import *


from main.TNR.TU.utils.ImageResizerTest import *
from main.TNR.TU.utils.ExtractPaginatorTest import *
from main.TNR.TU.utils.EmailSenderTest import *
from main.TNR.TU.utils.UrlsUtilsTest import *

from main.TNR.TU.utils.logger.LoggerFactoryTest import *


from main.TNR.TU.Service.FailedLoginAttemptServiceTest import *
from main.TNR.TU.Service.MusicServiceTest import *
from main.TNR.TU.Service.RandomizeTrackServiceTest import *
from main.TNR.TU.Service.RGPDServiceNotActiveTest import *
from main.TNR.TU.Service.RGPDServiceNotConfirmedTest import *
from main.TNR.TU.Service.ConfirmationUserServiceTest import *

from main.TNR.TU.UserParametersFactoryTest import *

from main.TNR.TU.config.PlaylistConfigTest import *

from main.TNR.TU.middleware.ErrorTrackingMiddlewareTest import *

# Create your tests here.
