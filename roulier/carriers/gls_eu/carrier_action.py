"""Implementation for Laposte."""
from ...carrier_action import CarrierGetLabel
from ...roulier import factory
from .encoder import GlsEuEncoder
from .decoder import GlsEuDecoderGetLabel
from .transport import GlsEuTransport
from .api import GlsEuApiParcel


class GlsEuGetabel(CarrierGetLabel):
    """Implementation for GLS via it's REST WebService."""

    ws_url = "https://api.gls-group.eu/public/v1/shipments"
    ws_test_url = "https://api-qs.gls-group.eu/public/v1/shipments"
    encoder = GlsEuEncoder
    decoder = GlsEuDecoderGetLabel
    transport = GlsEuTransport
    api = GlsEuApiParcel
    manage_multi_label = True


factory.register_builder("gls_eu", "get_label", GlsEuGetabel)
