# -*- coding: utf-8 -*-
"""Implementation for Dpd."""

from .dpd_decoder import DpdDecoder
from .dpd_encoder import DpdEncoder
from .dpd_transport import DpdTransport
from roulier.carrier import Carrier
from roulier import ws_tools as tools


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
        if not response['payload']:
            return response
        payload = self.decoder.decode(response, {})
        payload['zpl'] = self.handle_zpl(data, payload['label'])
        return payload

    # shortcuts
    def get_label(self, data):
        """Genereate a createShipmentWithLabels."""
        return self.get(data, 'createShipmentWithLabels')

    # utils
    def handle_zpl(self, data, png):
        if data['labelFormat'] == 'ZPL':
            zpl = tools.png_to_zpl(png, True)
        return zpl
