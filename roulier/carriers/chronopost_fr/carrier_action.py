"""Implementation for Chronopost."""
from ...carrier_action import CarrierGetLabel
from ...roulier import factory
from .encoder import ChronopostFrEncoder
from .decoder import ChronopostFrDecoder
from .transport import ChronopostFrRequestsTransport
from .api import ChronopostFrApiParcel


class ChronopostFrGetabel(CarrierGetLabel):
    """Implementation for Chronopost."""

    ws_url = "https://ws.chronopost.fr/shipping-cxf/ShippingServiceWS"
    encoder = ChronopostFrEncoder
    decoder = ChronopostFrDecoder
    transport = ChronopostFrRequestsTransport
    api = ChronopostFrApiParcel
    manage_multi_label = False


factory.register_builder("chronopost_fr", "get_label", ChronopostFrGetabel)
