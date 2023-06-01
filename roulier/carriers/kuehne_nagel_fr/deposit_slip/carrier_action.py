from roulier.carrier_action import CarrierGetEdi
from ..encoder import KuehneNagelFrEncoder
from .api import KuehneNagelDepositApi
from .transport import KuehneNagelFrTransportEDI
from ....roulier import factory


class KuehneNagelFrEDI(CarrierGetEdi):
    """Implementation for Kuehne+Nagel"""

    encoder = KuehneNagelFrEncoder
    transport = KuehneNagelFrTransportEDI
    api = KuehneNagelDepositApi


factory.register_builder("kuehne_nagel_fr", "get_edi", KuehneNagelFrEDI)
