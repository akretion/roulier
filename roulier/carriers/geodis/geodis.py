# -*- coding: utf-8 -*-
"""Implementation for Geodis."""
from geodis_encoder_edi import GeodisEncoderEdi
from geodis_encoder_ws import GeodisEncoderWs
from geodis_decoder import GeodisDecoder
from geodis_transport_ws import GeodisTransportWs
from geodis_transport_edi import GeodisTransportEdi
from roulier.carrier import Carrier
from roulier.exception import InvalidAction


class Geodis(Carrier):
    """Implementation for Geodis."""

    def api(self, action='label'):
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
        return self._get_ws(data, api, 'demandeImpressionEtiquette')

    def address_validator(self, data, api=False):
        return self._get_ws(data, api, 'findLocalite')

    def _get_ws(self, data, api=False, action=None):
        encoder = GeodisEncoderWs()
        decoder = GeodisDecoder()
        transport = GeodisTransportWs()

        if api:
            return encoder.api(action=action)

        request = encoder.encode(data, action)
        response = transport.send(request)
        return decoder.decode(
            response['body'],
            response['parts'],
            request['infos'],
        )

    ACTIONS = {
        'label': get_label,
        'findLocalite': address_validator,
        'demandeImpressionEtiquette': get_label,
        'edi': get_edi
    }