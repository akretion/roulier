"""Laposte XML -> Python."""

import base64
from datetime import datetime
from lxml import objectify

from roulier.codec import DecoderGetLabel

from .constants import SERVICE_PandR
from .constants import SERVICE_PandS


class GlsEuDecoderGetLabel(DecoderGetLabel):
    def decode(self, response, input_payload):
        without_label = "pickup" in input_payload["body"]["addresses"]
        """
        Decodes JSON returned by GLS and formats it to roulier standardization
        """
        body = response["body"]
        parcels = []
        annexes = []
        for gls_parcel in body["parcels"]:
            parcel = {
                "id": gls_parcel["parcelNumber"],
                "reference": gls_parcel["parcelNumber"],
                "tracking": {
                    "number": gls_parcel["trackId"],
                    "url": gls_parcel["location"],
                    "partner": "",
                },
            }
            if not without_label:
                parcel["label"] = {
                    "data": body["labels"][len(parcels)],
                    "name": "label_1",
                    "type": input_payload["body"].get("labelFormat", "PDF"),
                }
            parcels.append(parcel)
        self.result["parcels"] += parcels
        self.result["annexes"] += annexes
