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
        except:
            raise InvalidAction("Action not supported")
        return self[method](None, api=True)

    def get(self, data, action):
        """."""
        try:
            method = self.ACTIONS[action]
        except:
            raise InvalidAction("Action not supported")

        return self[method](data)

    def get_label(self, data, api=False):
        """Genereate a generateLabelRequest."""
        encoder = GeodisEncoderWs()
        decoder = GeodisDecoder()
        transport = GeodisTransportWs()

        if api:
            return encoder.api()

        request = encoder.encode(data, "generateLabelRequest")
        response = transport.send(request)
        return decoder.decode(
            response['body'],
            response['parts'],
            request['output_format'])

    def get_edi(self, data, api=False):
        encoder = GeodisEncoderEdi()
        transport = GeodisTransportEdi()
        if api:
            return encoder.api()
        arr = encoder.encode(data)
        return transport.send(arr)

    ACTIONS = {
        'label': get_label,
        'generateLabelRequest': get_label,
        'edi': get_edi
    }