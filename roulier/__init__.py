from . import roulier
from . import exception
from . import api
from . import codec
from . import transport
from . import carrier_action
from . import carriers
from . import carriersv2
import logging

__all__ = [roulier]
# __version__ = open('VERSION').read().strip()
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
