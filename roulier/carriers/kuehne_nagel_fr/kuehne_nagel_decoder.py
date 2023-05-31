# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class KuehneNagelDecoder(Decoder):
    """Mock class."""

    def decode(self, payload):
        """Return {}."""
        return {
            'label': {
                "name": "label",
                "data": payload['zpl'].encode('utf-8'),
                "type": 'zpl'
            },
            'deposit': {
                'line': payload['line'],
                'parcel': payload['parcel'],
                'footer': payload['footer'],
            },
            'tracking': {
                'parcel': payload['parcelNumber'],
                'number': payload['trackingNumber'],
            }
        }
