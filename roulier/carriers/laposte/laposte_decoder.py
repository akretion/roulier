# -*- coding: utf-8 -*-
"""Laposte XML -> Python."""
from lxml import objectify
from roulier.codec import Decoder


class LaposteDecoder(Decoder):
    """Laposte XML -> Python."""

    def decode(self, response, parts):
        payload_xml = response['payload']
        tag, content = self.decode_payload(payload_xml)
        if tag.endswith('getProductInterResponse'):
            return content
        else:
            # tag is generateLabelResponse
            label_cid = content.get('label').getchildren()[0].attrib['href']
            if content.get('cn23'):
                cn23_cid = content.get('cn23').getchildren()[0].attrib['href']
            else:
                cn23_cid = False
                content['cn23'] = False

            content['label'] = parts[label_cid.replace('cid:', '')]
            if cn23_cid:
                content['cn23'] = parts[cn23_cid.replace('cid:', '')]

        return content

    def decode_payload(self, xml_string):
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
                "cn23": msg.labelResponse.find('cn23'),
                "label": msg.labelResponse.find('label'),
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
        return tag, lookup[tag](xml.xpath('//return')[0])
