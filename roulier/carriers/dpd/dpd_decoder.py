# -*- coding: utf-8 -*-
"""Dpd XML -> Python."""
from lxml import objectify
from roulier.codec import Decoder


class DpdDecoder(Decoder):
    """Dpd XML -> Python."""

    def decode(self, response, parts):
        payload_xml = response['payload']
        tag, content = self.decode_payload(payload_xml)
        return content

    def decode_payload(self, xml_string):
        """Dpd XML -> Python."""
        def create_shipment_with_labels(msg):
            """Understand a CreateShipmentWithLabelsResponse."""
            shipments, labels = (
                msg.CreateShipmentWithLabelsResult.getchildren()
            )
            shipment = shipments.getchildren()[0]
            label, attachment = labels.getchildren()
            # .text because we want str instead of objectify.StringElement
            x = {
                'barcode': shipment.barcode.text,
                'parcelnumber': shipment.parcelnumber.text,
                'label': label.label.text,
                'attachment': attachment.label.text
            }
            return x

        xml = objectify.fromstring(xml_string)
        tag = xml.tag
        lookup = {
            "{http://www.cargonet.software}CreateShipmentWithLabelsResponse":
                create_shipment_with_labels,
        }
        return tag, lookup[tag](xml)
