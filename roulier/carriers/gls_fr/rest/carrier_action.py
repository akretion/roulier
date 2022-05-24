"""Implementation for Laposte."""

from roulier.carrier_action import CarrierGetLabel
from roulier.roulier import factory

from .api import GlsEuApiParcel
from .encoder import GlsEuEncoder
from .decoder import GlsEuDecoderGetLabel
from .transport import GlsEuTransport


class GlsEuGetabel(CarrierGetLabel):
    """Implementation for GLS via it's REST WebService."""

    ws_url = "https://api.gls-group.eu/public/v1/shipments"
    ws_test_url = "https://api-qs1.gls-group.eu/public/v1/shipments"
    encoder = GlsEuEncoder
    decoder = GlsEuDecoderGetLabel
    transport = GlsEuTransport
    api = GlsEuApiParcel
    manage_multi_label = True


factory.register_builder("gls_fr_rest", "get_label", GlsEuGetabel)
