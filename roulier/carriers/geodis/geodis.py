# -*- coding: utf-8 -*-
"""Implementation for Geodis."""

from .geodis_encoder_edi import GeodisEncoderEdi
from .geodis_encoder_ws import GeodisEncoderWs
from .geodis_encoder_rest_ws import GeodisEncoderRestWs
from .geodis_decoder_ws import GeodisDecoderWs
from .geodis_decoder_rest_ws import GeodisDecoderRestWs
from .geodis_transport_ws import GeodisTransportWs
from .geodis_transport_edi import GeodisTransportEdi
from .geodis_transport_rest_ws import GeodisTransportRestWs

from roulier.carrier import Carrier
from roulier.exception import InvalidAction

# Specifications:
# rest
#    usage: tracking
#    document: GEODIS - GUIDE TECHNIQUE SIC - Nouveau service Zoom - v1.1.docx
#    date: 2018
# edi:
#    usage: deposit slip
#    document: IFCSUM_D96A_1026_Client_Construit_FR.doc
#    date: 2012
# xml:
#    usage: label and findLocalite
#    document: GEODIS_Nouvelle eětiquette_GEOLABEL_v FR_V1.9.1.pdf
#    date: 2016


class Geodis(Carrier):
    """Implementation for Geodis."""

    def api(self, action="label"):
        """Expose how to communicate with Geodis."""
        try:
            method = self.ACTIONS[action]
        except KeyError:
            raise InvalidAction("Action not supported")
        return method(self, None, api=True)

    def get(self, data, action):
        """."""
        try:
            method = self.ACTIONS[action]
        except KeyError:
            raise InvalidAction("Action not supported")

        return method(self, data)

    def get_edi(self, data, api=False):
        encoder = GeodisEncoderEdi()
        transport = GeodisTransportEdi()
        if api:
            return encoder.api()
        arr = encoder.encode(data)
        return transport.send(arr)

    def get_label(self, data, api=False):
        """Genereate a demandeImpressionEtiquette."""
        return self._get_ws(data, api, "demandeImpressionEtiquette")

    def address_validator(self, data, api=False):
        return self._get_ws(data, api, "findLocalite")

    def get_tracking(self, data, api=False):
        return self._get_rest_ws(data, api, "tracking")

    def get_tracking_list(self, data, api=False):
        return self._get_rest_ws(data, api, "trackingList")

    def _get_ws(self, data, api=False, action=None):
        encoder = GeodisEncoderWs()
        decoder = GeodisDecoderWs()
        transport = GeodisTransportWs()

        if api:
            return encoder.api(action=action)

        request = encoder.encode(data, action)
        response = transport.send(request)
        return decoder.decode(response["body"], response["parts"], request["infos"],)

    def _get_rest_ws(self, data, api=False, action=None):
        encoder = GeodisEncoderRestWs()
        decode = GeodisDecoderRestWs()
        transport = GeodisTransportRestWs()
        if api:
            return encoder.api(action=action)
        request = encoder.encode(data, action)
        response = transport.send(request)
        return decode.decode(response, action)

    ACTIONS = {
        "label": get_label,
        "findLocalite": address_validator,
        "demandeImpressionEtiquette": get_label,
        "edi": get_edi,
        "tracking": get_tracking,
        "trackingList": get_tracking_list,
    }
