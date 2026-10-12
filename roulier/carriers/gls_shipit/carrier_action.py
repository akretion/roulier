"""Implementation for Laposte."""

from roulier.carrier_action import CarrierGetLabel
from roulier.roulier import factory

from .api import GlsShipItApiParcel
from .encoder import GlsShipItEncoder
from .decoder import GlsShipItDecoderGetLabel
from .transport import GlsShipItTransport


class GlsShipItGetabel(CarrierGetLabel):
    """Implementation for GLS via it's REST WebService."""

    ws_url = "https://api.gls-group.net"
    ws_test_url = "https://api-sandbox.gls-group.net"
    encoder = GlsShipItEncoder
    decoder = GlsShipItDecoderGetLabel
    transport = GlsShipItTransport
    api = GlsShipItApiParcel
    manage_multi_label = True


factory.register_builder("gls_shipit", "get_label", GlsShipItGetabel)
