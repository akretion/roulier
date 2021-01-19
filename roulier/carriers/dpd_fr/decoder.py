# -*- coding: utf-8 -*-
"""Dpd XML -> Python."""
from lxml import objectify
from roulier.codec import DecoderGetLabel
from roulier import ws_tools as tools
import base64


class DpdDecoder(DecoderGetLabel):
    """Dpd XML -> Python."""

    def decode(self, response, input_payload):
        """Understand a CreateShipmentWithLabelsResponse."""
        output_format = input_payload["output_format"]
        xml = objectify.fromstring(response["body"])
        shipments, files = xml.CreateShipmentWithLabelsResult.getchildren()
        shipment = shipments.getchildren()[0]
        label_file, summary_file = files.getchildren()
        parcel = {
            "id": 1,
            "reference": self._get_parcel_number(input_payload)
            or shipment.parcelnumber.text,
            "tracking": {"number": shipment.barcode.text, "url": "", "partner": "",},
            "label": {  # same as main label
                "data": label_file.label.text,
                "name": "label 1",
                "type": output_format,
            },
        }
        annexes = [
            {"data": summary_file.label.text, "name": "Summary", "type": output_format}
        ]
        self.result["parcels"].append(parcel)
        self.result["annexes"] += annexes
