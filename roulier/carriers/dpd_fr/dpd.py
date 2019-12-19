# -*- coding: utf-8 -*-
"""Implementation for Dpd."""

from .dpd_decoder import DpdDecoder
from .dpd_encoder import DpdEncoder
from .dpd_transport import DpdTransport
from roulier.carrier import Carrier
from roulier.exception import InvalidAction


class Dpd(Carrier):
    """Implementation for Dpd."""

    encoder = DpdEncoder()
    decoder = DpdDecoder()
    ws = DpdTransport()

    def api(self, action='label'):
        """Expose how to communicate with Dpd."""
        try:
            method = self.ACTIONS[action]
        except KeyError:
            raise InvalidAction("Action not supported")
        return method(self, None, api=True)


    def get(self, data, action, api):
        """Run an action with data against Dpd WS."""
        if api:
            return self.encoder.api(action)
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)
        return self.decoder.decode(response, request, action)

    # shortcuts
    def get_label(self, data, api=False):
        """Genereate a createShipmentWithLabels."""
        return self.get(data, 'createShipmentWithLabels', api)

    ACTIONS = {
        'label': get_label,
    }
