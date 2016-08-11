# -*- coding: utf-8 -*-
"""Implementation for Laposte."""
from laposte_encoder import LaposteEncoder
from laposte_decoder import LaposteDecoder
from laposte_transport import LaposteTransport
from roulier.carrier import Carrier


class Laposte(Carrier):
    """Implementation for Laposte."""

    encoder = LaposteEncoder()
    decoder = LaposteDecoder()
    ws = LaposteTransport()

    def api(self):
        """Expose how to communicate with a Laposte."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Laposte WS."""
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)
        if not response['payload']:
            return response
        parts = self.ws.get_parts(response['response'])
        return self.decoder.decode(response, parts)

    # shortcuts
    def get_label(self, data):
        """Genereate a generateLabelRequest."""
        return self.get(data, 'generateLabelRequest')
