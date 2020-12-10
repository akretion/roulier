# -*- coding: utf-8 -*-
"""Laposte XML -> Python."""
from lxml import objectify

from ...codec import DecoderGetLabel
import base64


class LaposteFrDecoderGetLabel(DecoderGetLabel):
    """Laposte XML -> Python."""

    def decode(self, response, input_payload):
        """Laposte XML -> Python."""
        body = response["body"]
        parts = response["parts"]
        output_format = input_payload["output_format"]

        xml = objectify.fromstring(body)
        msg = xml.xpath("//return")[0]

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
            data = parts.get(cn23_cid)
            annexes.append(
                {"name": "cn23", "data": base64.b64encode(data), "type": "pdf"}
            )

        if rep.find("pdfUrl"):
            annexes.append({"name": "label", "data": rep.find("pdfUrl"), "type": "url"})

        parcel = {
            "id": 1,  # no multi parcel management for now.
            "reference": self._get_parcel_number(input_payload),
            "tracking": {
                "number": rep.parcelNumber,
                "url": "",
                "partner": rep.find("parcelNumberPartner"),
            },
            "label": {
                "data": base64.b64encode(parts.get(label_cid)),
                "name": "label_1",
                "type": output_format,
            },
        }
        self.result["parcels"].append(parcel)
        self.result["annexes"] += annexes
