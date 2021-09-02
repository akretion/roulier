"""Implementation for UPS."""

from roulier.roulier import factory
from roulier.carrier_action import CarrierGetLabel

from .api import UpsApi
from .decoder import UpsDecoder
from .encoder import UpsEncoder
from .transport import UpsTransport


class UpsRestGetabel(CarrierGetLabel):
    """Implementation for UPS."""

    ws_url = "https://onlinetools.ups.com/ship/v1807/shipments"
    ws_test_url = "https://wwwcie.ups.com/ship/v1807/shipments"
    encoder = UpsEncoder
    decoder = UpsDecoder
    transport = UpsTransport
    api = UpsApi
    manage_multi_label = True


factory.register_builder("ups_rest", "get_label", UpsRestGetabel)
