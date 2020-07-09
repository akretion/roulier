# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from roulier.codec import Decoder
from .geodis_api_rest_ws import GeodisApiTrackingListOut


class GeodisDecoderRestWs(Decoder):
    """Geodis XML -> Python."""

    def decode(self, payload, action):
        """Geodis JSON -> Python.
        payload[body] : dict
        payload[request] : Requests obj
        """
        body = payload["body"]
        if action == "trackingList":
            mapping = GeodisApiTrackingListOut()
            formatted = []
            for line in body:
                self.add_tracking_code(line)
                formatted.append(mapping.normalize(line))
        else:
            # NOT implemented
            formatted = body
        return formatted

    def add_tracking_code(self, data):
        # MVL: mise en livraison
        # AAR: en cours acheminement
        # None: en attente prise en charge
        # LIV: livré
        # CFM: conforme
        if data["codeSituation"] == "LIV":
            state = "DELIVERED"
        elif data["codeSituation"] == "SOL":
            state = "RETURNED"
        elif data["codeSituation"] in ("MLV", "AAR"):
            state = "TRANSIT"
        else:
            state = "UNKNOWN"
        data["status"] = state


# CODES=
# 'UNKNOWN',
# 'DELIVERED',
# 'TRANSIT',
# 'FAILURE',
# 'RETURNED'
