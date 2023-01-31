from roulier.carrier_action import CarrierWebservice
from roulier.roulier import factory
from .encoder import GeodisEncoderRestWs
from .decoder import GeodisFrTrackingListDecoder, GeodisFrTrackingDecoder
from ..geodis_transport_rest import GeodisTransportRestWs
from .api import GeodisApiTracking, GeodisApiTrackingList


class GeodisFrTrackingList(CarrierWebservice):

    ws_url = "https://espace-client.geodis.com/services/api/zoomclient/recherche-envois"
    service = "api/zoomclient/recherche-envois"
    encoder = GeodisEncoderRestWs
    decoder = GeodisFrTrackingListDecoder
    transport = GeodisTransportRestWs
    api = GeodisApiTrackingList

    def get_tracking_list(self, carrier_type, action, data):
        return self._get_data_from_webservice(data)


factory.register_builder("geodis_fr", "get_tracking_list", GeodisFrTrackingList)


class GeodisFrTracking(CarrierWebservice):

    ws_url = "https://espace-client.geodis.com/services/api/zoomclient/recherche-envoi"
    service = "api/zoomclient/recherche-envoi"
    encoder = GeodisEncoderRestWs
    decoder = GeodisFrTrackingDecoder
    transport = GeodisTransportRestWs
    api = GeodisApiTracking

    def get_tracking(self, carrier_type, action, data):
        return self._get_data_from_webservice(data)


factory.register_builder("geodis_fr", "get_tracking", GeodisFrTrackingList)
