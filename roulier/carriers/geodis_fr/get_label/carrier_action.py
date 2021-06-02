from roulier.carrier_action import CarrierGetLabel
from roulier.roulier import factory
from .encoder import GeodisFrParcelEncoder
from .decoder import GeodisFrParcelDecoder
from ..geodis_soap_transport import GeodisFrSoapTransport
from .api import GeodisFrParcelApi


class GeodisFrGetabel(CarrierGetLabel):
    """Implementation for Chronopost."""

    label_formats = {
        "ZPL": ("Z", "zpl"),
        "PDF": ("P", "pdf"),
        "HTML": ("H", "html"),
        "XML": ("X", "xml"),
        "EPL2": ("E", "epl"),
        "Z": ("Z", "zpl"),
        "P": ("P", "pdf"),
        "H": ("H", "html"),
        "X": ("X", "xml"),
        "E": ("E", "epl"),
    }
    xmlns = "http://impression.service.web.etiquette.geodis.com"
    ws_url = "https://espace.geodis.com/geolabel/services/ImpressionEtiquette"
    ws_test_url = (
        "https://espace-rct.geodis.com/geolabel/services/ImpressionEtiquette"  # nopep8
    )
    encoder = GeodisFrParcelEncoder
    decoder = GeodisFrParcelDecoder
    transport = GeodisFrSoapTransport
    api = GeodisFrParcelApi
    manage_multi_label = True


factory.register_builder("geodis_fr", "get_label", GeodisFrGetabel)
