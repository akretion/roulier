# -*- coding: utf-8 -*-
"""Laposte XML -> Python."""
import email.parser
from lxml import objectify
from roulier.codec import Decoder


class LaposteDecoder(Decoder):
    """Laposte XML -> Python."""

    def get_parts(self, response):
        head_lines = ''
        for k, v in response.raw.getheaders().iteritems():
            head_lines += str(k)+':'+str(v)+'\n'

        full = head_lines + response.content

        parser = email.parser.Parser()
        decoded_reply = parser.parsestr(full)
        parts = {}
        start = decoded_reply.get_param('start').lstrip('<').rstrip('>')
        i = 0
        for part in decoded_reply.get_payload():
            cid = part.get('content-Id', '').lstrip('<').rstrip('>')
            if (not start or start == cid) and 'start' not in parts:
                parts['start'] = part.get_payload()
            else:
                parts[cid or 'Attachment%d' % i] = part.get_payload()
            i += 1

        return parts

    def decode(self, response):
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

            parts_dict = self.get_parts(response['response'])
            content['label'] = parts_dict[label_cid.replace('cid:', '')]
            if cn23_cid:
                content['cn23'] = parts_dict[cn23_cid.replace('cid:', '')]

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
                "url": msg.labelResponse.pdfUrl,
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
