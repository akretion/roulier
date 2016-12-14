# -*- coding: utf-8 -*-
"""Implementation for Dpd."""

from .dpd_decoder import DpdDecoder
from .dpd_encoder import DpdEncoder
from .dpd_transport import DpdTransport
from .dpd_api import DpdApi
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
        zpl = self.handle_zpl(data, payload['label'])
        payload['label'] = zpl if zpl else payload['label']
        return payload

    # shortcuts
    def get_label(self, data):
        """Genereate a createShipmentWithLabels."""
        return self.get(data, 'createShipmentWithLabels')

    # utils
    def handle_zpl(self, data, png):
        """Convert a png in zpl.

        if labelFormat was asked as ZPL, WS returns a png
        This function rotate it and convert it an suitable zpl format
        @params:
            data : full dict with all the params of the get method
            png : a base64 formatted string (returned by ws)
        @returns:
            a zpl in a string

        """
        label_format = DpdApi().normalize(data)['service']['labelFormat']

        if label_format == 'ZPL':
            return tools.png_to_zpl(png, True)
        return None
