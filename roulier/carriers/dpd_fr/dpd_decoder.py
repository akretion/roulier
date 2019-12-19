# -*- coding: utf-8 -*-
"""Dpd XML -> Python."""
from roulier.codec import Decoder
from .dpd_api import DpdApiGetLabelMappingOut
from exceptions import NotImplementedError


class DpdDecoder(Decoder):
    """Dpd json response -> Python."""


    def decode(self, payload, request, action):
        """Dpd JSON -> Python.
        payload: response as dict
        request: requests
        """
        if action == 'createShipmentWithLabels':
            mapping = DpdApiGetLabelMappingOut()
            return mapping.normalize(payload, request)
        else:
            raise NotImplementedError(action)
