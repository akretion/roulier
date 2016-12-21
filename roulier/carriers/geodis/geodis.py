# -*- coding: utf-8 -*-
"""Implementation for Geodis."""
from geodis_encoder import GeodisEncoder
from geodis_decoder import GeodisDecoder
from geodis_transport import GeodisTransport
from roulier.carrier import Carrier


class Geodis(Carrier):
    """Implementation for Geodis."""

    encoder = GeodisEncoder()
    decoder = GeodisDecoder()
    ws = GeodisTransport()

    def api(self):
        """Expose how to communicate with Geodis."""
        return self.encoder.api()

    def get(self, data, action):
        """Run an action with data against Geodis WS."""
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)
        if response['status'] == 'error':
            return response
        parts = response['attachement']
        return self.decoder.decode(response, parts)

    # shortcuts
    def get_label(self, data):
        """Genereate a generateLabelRequest."""
        return self.get(data, 'demandeImpressionEtiquette')
