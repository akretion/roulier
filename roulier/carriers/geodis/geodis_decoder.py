# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from lxml import objectify
from roulier.codec import Decoder


class GeodisDecoder(Decoder):
    """Geodis XML -> Python."""

    def decode(self, response, parts):
        payload_xml = response['payload']
        tag, content = self.decode_payload(payload_xml, parts)

        return content

    def decode_payload(self, payload, parts):
        """Geodis XML -> Python."""

        def reponse_impression_etiquette(msg, parts):
            x = {
                'barcode': payload.infoColis.cab,
                'cab': payload.cabRouting,
                'label': parts,
            }
            return x

        tag = payload.tag
        lookup = {
            "{http://impression.service.web.etiquette.geodis.com}reponseImpressionEtiquette":
                reponse_impression_etiquette,
        }
        return tag, lookup[tag](payload, parts)
