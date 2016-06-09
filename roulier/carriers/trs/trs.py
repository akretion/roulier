# -*- coding: utf-8 -*-
"""Implementation for trs."""
from trs_encoder import TrsEncoder
from trs_decoder import TrsDecoder
from trs_transport import TrsTransport
from roulier.carrier import Carrier


class Trs(Carrier):
    """Implementation for trs."""

    encoder = TrsEncoder()
    decoder = TrsDecoder()
    ws = TrsTransport()

    def api(self):
        """Expose how to communicate with trs."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action."""
        if action == "generateLabel":
            return self.get_label(data)
        if action == "deliverySlip":
            return self.get_delivery_slip(data)
        raise Exception(
            'action %s not in %s' % (
                action, ', '.join(self.encoder.TRS_ACTIONS)))

    def get_label(self, data):
        """Generate a label."""
        request = self.encoder.encode(data, 'generateLabel')
        response = self.ws.send(request)

        if not response['payload']:
            return response
        return self.decoder.decode(response['payload'])

    def get_delivery_slip(self, data):
        """Generate a delivery slip (csv file)."""
        return self.ws.generate_delivery_slip(data)
