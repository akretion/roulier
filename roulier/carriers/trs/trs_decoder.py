# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class TrsDecoder(Decoder):
    """Prepare output"""

    def decode(self, response, request):
        """Return {}."""

        return {
            'label': response['payload'],
            'tracking_number': request['body']['service']['shippingId'],
            'tracking_url': '',
            'annexes': [
                {
                    'name': 'meta',
                    'type': 'csv',
                    'data': response['attachment']
                }
            ]
        }
