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
            shipments, labels = msg.CreateShipmentWithLabelsResult
            shipment = shipments.getchildren()[0]
            label, attachment = labels.getChildren()
            x = {
                'barcode': shipment.barcode,
                'parcelnumber': shipment.parcelnumber,
                'label': label.label,
                'attachment': attachment.label
            }
            return x

        xml = objectify.fromstring(xml_string)
        tag = xml.tag
        lookup = {
            "{http://www.cargonet.software}CreateShipmentWithLabelsResponse":
                create_shipment_with_labels,
        }
        return tag, lookup[tag]()
