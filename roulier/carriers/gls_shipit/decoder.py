"""Laposte XML -> Python."""

import base64
from datetime import datetime
from lxml import objectify

from roulier.codec import DecoderGetLabel

from .constants import SERVICE_PandR
from .constants import SERVICE_PandS


class GlsShipItDecoderGetLabel(DecoderGetLabel):
    def decode(self, response, input_payload):
        without_label = False
        """
        Decodes JSON returned by GLS and formats it to roulier standardization
        """
        body = response["body"]
        parcels = []
        annexes = []
        for gls_parcel in body["CreatedShipment"]["ParcelData"]:
            parcel = {
                "id": gls_parcel.get("ParcelNumber"),
                "reference": gls_parcel.get("PartnerParcelNumber")
                or gls_parcel["ParcelNumber"],
                "tracking": {
                    "number": gls_parcel["TrackID"],
                    "url": "https://gls-group.eu/GROUP/en/parcel-tracking?match="
                    + gls_parcel["TrackID"],
                    "partner": "",
                },
            }
            parcels.append(parcel)
        nb_parcels = len(parcels)
        for offset, gls_print in enumerate(
            body["CreatedShipment"].get("PrintData", [])
        ):
            label = {
                "data": gls_print["Data"],
                "name": f"label_{offset+1}",
                "type": gls_print.get("LabelFormat ", "PDF"),
            }
            if offset >= nb_parcels:
                annexes.append(label)
            else:
                parcels[offset]["label"] = label
        self.result["parcels"] += parcels
        self.result["annexes"] += annexes
