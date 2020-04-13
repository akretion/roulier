# -*- coding: utf-8 -*-
"""Laposte XML -> Python."""
from lxml import objectify

from ...roulier import Decoder
from .common import CARRIER_TYPE
import base64


class LaposteFrDecoder(Decoder):
    _carrier_type = CARRIER_TYPE
    _action = ["get_label"]

    """Laposte XML -> Python."""

    def decode(self, response, input_payload):
        """Laposte XML -> Python."""
        body = response["body"]
        parts = response["parts"]
        output_format = input_payload["output_format"]

        def get_product_inter(msg):
            """Understand a getProductInterResponse."""
            x = {"product": msg.product, "partnerType": msg.partnerType}
            return x

        def generate_label_response(msg):
            """Understand a generateLabelResponse."""

            def get_cid(tag, tree):
                element = tree.find(tag)
                if element is None:
                    return None
                href = element.getchildren()[0].attrib["href"]
                # href contains cid:236212...-38932@cfx.apache.org
                return href[len("cid:") :]  # remove prefix

            rep = msg.labelResponse
            cn23_cid = get_cid("cn23", rep)
            label_cid = get_cid("label", rep)

            annexes = []

            if cn23_cid:
                annexes.append(
                    {"name": "cn23", "data": parts.get(cn23_cid), "type": "pdf"}
                )

            if rep.find("pdfUrl"):
                annexes.append(
                    {"name": "label", "data": rep.find("pdfUrl"), "type": "url"}
                )

            return {
                "parcels": [
                    {
                        "id": 1,  # no multi parcel management for now.
                        "reference": rep.parcelNumber,
                        "tracking": {
                            "number": rep.parcelNumber,
                            "url": "",
                            "partner": rep.find("parcelNumberPartner"),
                        },
                        "label": {
                            "data": base64.b64encode(parts.get(label_cid).encode()),
                            "name": "label_1",
                            "type": output_format,
                        },
                    }
                ],
                "annexes": [],
            }

        xml = objectify.fromstring(body)
        tag = xml.tag
        lookup = {
            "{http://sls.ws.coliposte.fr}getProductInterResponse": get_product_inter,
            "{http://sls.ws.coliposte.fr}generateLabelResponse": generate_label_response,
        }
        return lookup[tag](xml.xpath("//return")[0])
