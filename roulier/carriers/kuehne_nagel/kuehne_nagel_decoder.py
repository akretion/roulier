# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class KuehneNagelDecoder(Decoder):
    """Mock class."""

    def decode(self, payload):
        """Return {}."""
        return {
            'epl': payload['epl'],
            'line': payload['line'],
            'parcel': payload['parcel'],
            'footer': payload['footer']
        }
