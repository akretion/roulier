# -*- coding: utf-8 -*-
"""UPS response -> Python."""
from roulier.codec import Decoder
import base64


class UpsDecoder(Decoder):

    def decode(self, response):
        result = {
            "tracking": {
                "number": response.get('ShipmentResponse').get("ShipmentResults").get("ShipmentIdentificationNumber"),
            },
            "parcels": [],
            "annexes": []}
        all_labels_data = response.get('ShipmentResponse').get("ShipmentResults").get("PackageResults")
        if isinstance(all_labels_data, dict):
            all_labels_data = [all_labels_data]
        i = 1
        for label_data in all_labels_data:
            result["parcels"].append({
                "id": i,
                "number": label_data.get("TrackingNumber"),
                "reference": "",
                "label": {  # same as main label
                    "name": label_data.get("TrackingNumber"),
                    "data": base64.b64decode(label_data.get("ShippingLabel").get("GraphicImage")),
                    "type": label_data.get('ShippingLabel').get("ImageFormat").get("Code").lower(),
                }
            })
            i += 1
        return result
