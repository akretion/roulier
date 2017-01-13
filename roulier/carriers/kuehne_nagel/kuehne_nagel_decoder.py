# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class KuehneNagelDecoder(Decoder):
    """Mock class."""

    def decode(self, payload):
        """Return {}."""
        return {
            'zpl': payload['zpl'].encode('utf-8'),
            'line': payload['line'],
            'parcel': payload['parcel'],
            'footer': payload['footer'],
            'parcelNumber': payload['parcelNumber'],
            'trackingNumber': payload['trackingNumber'],

        }
