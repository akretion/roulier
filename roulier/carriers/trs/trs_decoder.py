# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class TrsDecoder(Decoder):
    """Mock class."""

    def decode(self, payload):
        """Return {}."""
        return {"zpl": payload['zpl'], 'meta': payload['meta']}
