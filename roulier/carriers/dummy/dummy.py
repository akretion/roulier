# -*- coding: utf-8 -*-
"""Implementation for dummy."""
from .dummy_encoder import DummyEncoder
from .dummy_decoder import DummyDecoder
from .dummy_transport import DummyTransport
from roulier.carrier import Carrier


class Dummy(Carrier):
    """Implementation for dummy."""

    encoder = DummyEncoder()
    decoder = DummyDecoder()
    ws = DummyTransport()

    def api(self):
        """Expose how to communicate with dummy."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Laposte WS."""
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)

        if not response['payload']:
            return response
        return self.decoder.decode(response['payload'])

    # shortcuts
    def get_label(self, data):
        """Generate a label."""
        return self.get(data, 'generateLabel')
