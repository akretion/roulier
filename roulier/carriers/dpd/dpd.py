# -*- coding: utf-8 -*-
"""Implementation for Dpd."""

from .dpd_decoder import DpdDecoder
from .dpd_encoder import DpdEncoder
from .dpd_transport import DpdTransport
from roulier.carrier import Carrier


class Dpd(Carrier):
    """Implementation for Dpd."""

    encoder = DpdEncoder()
    decoder = DpdDecoder()
    ws = DpdTransport()

    def api(self):
        """Expose how to communicate with a Dpd."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Dpd WS."""
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)
        return self.decoder.decode(
            response['body'], request['output_format'])

    # shortcuts
    def get_label(self, data):
        """Genereate a createShipmentWithLabels."""
        return self.get(data, 'createShipmentWithLabels')
