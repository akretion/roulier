# -*- coding: utf-8 -*-
"""Mock class."""
from roulier.codec import Decoder


class DummyDecoder(Decoder):
    """Mock class."""

    def decode(self, zpl_string):
        """Return {}."""
        return {"zpl": zpl_string}
