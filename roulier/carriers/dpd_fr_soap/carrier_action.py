"""Implementation for Dpd."""

from roulier.roulier import factory
from roulier.carrier_action import CarrierGetLabel

from .api import DpdApi
from .decoder import DpdDecoder
from .encoder import DpdEncoder
from .transport import DpdTransport


class DpdGetabel(CarrierGetLabel):
    """Implementation for Dpd."""

    ws_url = (
        "https://e-station.cargonet.software/dpd-eprintwebservice/eprintwebservice.asmx"
    )
    ws_test_url = (
        "https://e-station-testenv.cargonet.software/exa-eprintwebservice/eprintwebservice.asmx?WSDL"
    )
    encoder = DpdEncoder
    decoder = DpdDecoder
    transport = DpdTransport
    api = DpdApi
    manage_multi_label = False


factory.register_builder("dpd_fr_soap", "get_label", DpdGetabel)
