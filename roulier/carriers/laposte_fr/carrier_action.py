"""Implementation for Laposte."""
from ...carrier_action import CarrierGetLabel
from ...roulier import factory
from .encoder import LaposteFrEncoder
from .decoder import LaposteFrDecoderGetLabel
from .transport import LaposteFrTransport
from .api import LaposteFrApiParcel


class LaposteFrGetabel(CarrierGetLabel):
    """Implementation for Laposte."""

    ws_url = "https://ws.colissimo.fr/sls-ws/SlsServiceWS"
    encoder = LaposteFrEncoder
    decoder = LaposteFrDecoderGetLabel
    transport = LaposteFrTransport
    api = LaposteFrApiParcel
    manage_multi_label = False


factory.register_builder("laposte_fr", "get_label", LaposteFrGetabel)
