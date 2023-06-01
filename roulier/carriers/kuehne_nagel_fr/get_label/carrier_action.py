from .api import KuehneNagelFrParcelApi
from ..encoder import KuehneNagelFrEncoder
from roulier.codec import Encoder
from ....roulier import factory
from roulier.carrier_action import CarrierGetLabel
from .decoder import KuehneNagelFrDecoderGetLabel
from .transport import KuehneNagelFrTransportLabel


class KuehneNagelFrGetabel(CarrierGetLabel):
    """Implementation for Kuehne+Nagel"""

    ws_url = False
    manage_multi_label = True
    encoder = KuehneNagelFrEncoder
    decoder = KuehneNagelFrDecoderGetLabel
    transport = KuehneNagelFrTransportLabel
    api = KuehneNagelFrParcelApi


factory.register_builder("kuehne_nagel_fr", "get_label", KuehneNagelFrGetabel)
