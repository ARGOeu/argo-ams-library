import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(NullHandler())

from .ams import ArgoMessagingService
from .amsexceptions import (AmsServiceException, AmsConnectionException, AmsException)
from .amsmsg import AmsMessage
