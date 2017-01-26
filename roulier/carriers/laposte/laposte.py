# -*- coding: utf-8 -*-
"""Implementation for Laposte."""

from .laposte_encoder import LaposteEncoder
from .laposte_decoder import LaposteDecoder
from .laposte_transport import LaposteTransport
from roulier.carrier import Carrier


class Laposte(Carrier):
    """Implementation for Laposte."""

    encoder = LaposteEncoder()
    decoder = LaposteDecoder()
    ws = LaposteTransport()

    def api(self):
        """Expose how to communicate with Laposte."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Laposte WS."""
        request = self.encoder.encode(data, action)
        xml_request, ws_response = self.ws.send(request)
        if ws_response.get('status') == self.ws.STATUS_ERROR:
            return ws_response
        parts = self.ws.get_parts(ws_response['response'])
        response = self.decoder.decode(ws_response, parts)
        response['xml_request'] = xml_request
        return response

    # shortcuts
    def get_label(self, data):
        """Genereate a generateLabelRequest."""
        return self.get(data, 'generateLabelRequest')
