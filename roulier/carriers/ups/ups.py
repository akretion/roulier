# -*- coding: utf-8 -*-
"""Implementation for Ups."""

from .ups_decoder import UpsDecoder
from .ups_encoder import UpsEncoder
from .ups_transport import UpsTransport
from roulier.carrier import Carrier


class Ups(Carrier):
    """Implementation for UPS."""

    encoder = UpsEncoder()
    decoder = UpsDecoder()
    ws = UpsTransport()

    def api(self):
        """Expose how to communicate with a Ups."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Ups WS."""
        request, header = self.encoder.encode(data, action)
        response = self.ws.send(request, header)
        return self.decoder.decode(
            response)

    # shortcuts
    def get_label(self, data):
        """Genereate a createShipmentWithLabels."""
        return self.get(data, 'createShipmentWithLabels')
