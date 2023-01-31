from roulier.carrier_action import CarrierAddressValidation
from roulier.roulier import factory
from .encoder import GeodisFrFindLocaliteEncoder
from .decoder import GeodisFrValidateAddressDecoder
from ..geodis_soap_transport import GeodisFrSoapTransport
from .api import GeodisApiFindLocaliteWs


class GeodisFrAddressValidation(CarrierAddressValidation):
    """Implementation for Geodis."""

    xmlns = "http://localite.service.web.etiquette.geodis.com"
    ws_url = "https://espace.geodis.com/geolabel/services/RechercherLocalite"
    ws_test_url = (
        "https://espace-rct.geodis.com/geolabel/services/RechercherLocalite"  # nopep8
    )
    encoder = GeodisFrFindLocaliteEncoder
    decoder = GeodisFrValidateAddressDecoder
    transport = GeodisFrSoapTransport
    api = GeodisApiFindLocaliteWs


factory.register_builder("geodis_fr", "validate_address", GeodisFrAddressValidation)
