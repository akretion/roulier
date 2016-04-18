# -*- coding: utf-8 -*-
"""Laposte XML -> Python."""
from lxml import objectify
from roulier.codec import Decoder


class LaposteDecoder(Decoder):
    """Laposte XML -> Python."""

    def decode(self, xml_string):
        """Laposte XML -> Python."""
        def get_product_inter(msg):
            """Understand a getProductInterResponse."""
            x = {
                "product": msg.product,
                "partnerType": msg.partnerType
            }
            return x

        def generate_label_response(msg):
            """Understand a generateLabelResponse."""
            x = {
                "parcelNumber": msg.labelResponse.parcelNumber,
                "parcelNumberPartner": msg.labelResponse.find(
                    'parcelNumberPartner'),
                "url": msg.labelResponse.pdfUrl,
                "cn23": msg.labelResponse.find('cn23'),
            }
            return x

        xml = objectify.fromstring(xml_string)
        tag = xml.tag
        lookup = {
            "{http://sls.ws.coliposte.fr}getProductInterResponse":
                get_product_inter,
            "{http://sls.ws.coliposte.fr}generateLabelResponse":
                generate_label_response
        }

        return lookup[tag](xml.xpath('//return')[0])
