# -*- coding: utf-8 -*-
"""Implementation for Dpd."""

from .api import DpdApi
from .decoder import DpdDecoder
from .encoder import DpdEncoder
from .transport import DpdTransport
from ...roulier import factory
from ...carrier_action import CarrierGetLabel


class DpdGetabel(CarrierGetLabel):
    """Implementation for Dpd."""

    ws_url = (
        "https://e-station.cargonet.software/dpd-eprintwebservice/eprintwebservice.asmx"
    )
    ws_test_url = (
        "http://92.103.148.116/exa-eprintwebservice/eprintwebservice.asmx?WSDL"
    )
    encoder = DpdEncoder
    decoder = DpdDecoder
    transport = DpdTransport
    api = DpdApi
    manage_multi_label = False


factory.register_builder("dpd_fr", "get_label", DpdGetabel)
