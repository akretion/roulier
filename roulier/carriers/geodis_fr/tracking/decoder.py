"""Geodis XML -> Python."""
from roulier.codec import DecoderBase
from .api import GeodisApiTrackingListOut


class GeodisFrTrackingListDecoder(DecoderBase):
    """Geodis XML -> Python."""

    def decode(self, response, input_payload):
        """Geodis JSON -> Python.
        payload[body] : dict
        payload[request] : Requests obj
        """
        body = response["body"]
        mapping = GeodisApiTrackingListOut(self.config)
        self.result = []
        for line in body:
            self.add_tracking_code(line)
            self.result.append(mapping.normalize(line))

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


class GeodisFrTrackingDecoder(DecoderBase):
    """Geodis XML -> Python."""

    def decode(self, response, input_payload):
        """Geodis JSON -> Python.
        payload[body] : dict
        payload[request] : Requests obj
        """
        body = response["body"]
        # NOT implemented
        self.result = body
