"""Implementation for Laposte."""

from roulier.carrier_action import CarrierGetLabel
from roulier.roulier import factory

from .encoder import GlsEncoder
from .decoder import GlsDecoder
from .transport import GlsTransport
from .api import GlsApiParcel


class GlsFrGetabel(CarrierGetLabel):
    """Implementation for Laposte."""

    ws_url = "http://www.gls-france.com/cgi-bin/glsboxGI.cgi"
    ws_test_url = "http://www.gls-france.com/cgi-bin/glsboxGITest.cgi"
    encoder = GlsEncoder
    decoder = GlsDecoder
    transport = GlsTransport
    api = GlsApiParcel
    manage_multi_label = False
    web_service_coding = "ISO-8859-1"


factory.register_builder("gls_fr_glsbox", "get_label", GlsFrGetabel)
