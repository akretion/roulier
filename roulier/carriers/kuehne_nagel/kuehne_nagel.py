# -*- coding: utf-8 -*-
"""Implementation for Kuehne & Nagel."""
from .kuehne_nagel_encoder import KuehneNagelEncoder
from .kuehne_nagel_decoder import KuehneNagelDecoder
from .kuehne_nagel_transport import KuehneNagelTransport
from roulier.carrier import Carrier


class KuehneNagel(Carrier):
    """Implementation for Kuehne & Nagel."""

    encoder = KuehneNagelEncoder()
    decoder = KuehneNagelDecoder()
    ws = KuehneNagelTransport()

    def api(self):
        """Expose how to communicate with kuehne & nagel."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action."""
        if action == "generateLabel":
            return self.get_label(data)
        if action == "depositSlip":
            return self.get_deposit_slip(data)
        raise Exception(
            'action %s not in %s' % (
                action, ', '.join(self.encoder.KUEHNE_ACTIONS)))

    def get_label(self, data):
        """Generate a label."""
        request = self.encoder.encode(data, 'generateLabel')
        response = self.ws.send(request)

        if not response['payload']:
            return response
        return self.decoder.decode(response['payload'])

    def get_deposit_slip(self, data):
        """Generate a deposit slip (txt file)."""
        data = self.encoder.encode(data, 'generateDepositSlip')
        return self.ws.generate_deposit_slip(data)
