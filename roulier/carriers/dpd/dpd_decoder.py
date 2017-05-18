# -*- coding: utf-8 -*-
"""Dpd XML -> Python."""
from lxml import objectify
from roulier.codec import Decoder
from roulier import ws_tools as tools
import base64


class DpdDecoder(Decoder):
    """Dpd XML -> Python."""

    def decode(self, body, output_format):
        """Dpd XML -> Python."""
        def create_shipment_with_labels(msg):
            """Understand a CreateShipmentWithLabelsResponse."""
            shipments, labels = (
                msg.CreateShipmentWithLabelsResult.getchildren()
            )
            shipment = shipments.getchildren()[0]
            label, attachment = labels.getchildren()
            label_data = self.handle_zpl(label.label.text, output_format)
            # .text because we want str instead of objectify.StringElement
            summary_data = base64.b64decode(attachment.label.text)
            summary_format = output_format == 'ZPL' and 'png' or output_format
            x = {
                "tracking": {
                    'number': shipment.barcode.text,
                },
                "parcels": [{
                    "id": 1,
                    "reference": "",
                    "number": shipment.parcelnumber.text,
                    "label": {  # same as main label
                        "data": label_data,
                        "name": "label 1",
                        "type": output_format,
                    }
                }],
                "label": {  # main label
                    "data": label_data,
                    "name": "label",
                    "type": output_format,
                },
                "annexes": [{
                    "data": summary_data,
                    "name": "Summary",
                    "type": summary_format
                }]
            }
            return x

        xml = objectify.fromstring(body)
        tag = xml.tag
        lookup = {
            "{http://www.cargonet.software}CreateShipmentWithLabelsResponse":
                create_shipment_with_labels,
        }
        return lookup[tag](xml)

    def handle_zpl(self, png, label_format):
        """Convert a png in zpl.

        if labelFormat was asked as ZPL, WS returns a png
        This function rotate it and convert it an suitable zpl format
        """
        if label_format == 'ZPL':
            return tools.png_to_zpl(png, True)
        else:
            return base64.b64decode(png)
