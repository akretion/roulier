from roulier.carrier_action import CarrierGetEdi
from roulier.roulier import factory
from .encoder import GeodisFrEncoderEdi
from .transport import GeodisTransportEdi
from .api import GeodisFrApiEdi


class GeodisFrEdi(CarrierGetEdi):
    """Implementation for Geodis."""

    encoder = GeodisFrEncoderEdi
    transport = GeodisTransportEdi
    api = GeodisFrApiEdi


factory.register_builder("geodis_fr", "get_edi", GeodisFrEdi)
