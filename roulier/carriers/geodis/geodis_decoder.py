# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from roulier.codec import Decoder


class GeodisDecoder(Decoder):
    """Geodis XML -> Python."""

    def decode(self, body, parts, output_format):
        """Geodis XML -> Python."""

        def reponse_impression_etiquette(msg, parts):
            x = {
                "tracking": {
                    "barcode": body.cabRouting,
                },
                "label": {
                    "name": "label",
                    "data": parts,
                    "type": output_format
                },
                "annexes": [
                ],
                "extra": {
                    "reseau": body.reseau,
                    "priorite": body.priorite,
                    "codeDirectionel": body.codire,
                    "cabRouting": body.cabRouting,
                    "colis": {
                        "codeUmg": body.infoColis.codumg,
                        "numero": body.infoColis.numero,
                        "cab": body.infoColis.cab,
                    }
                }
            }
            return x

        tag = body.tag
        lookup = {
            "{http://impression.service.web.etiquette.geodis.com}reponseImpressionEtiquette":
                reponse_impression_etiquette,
        }
        return lookup[tag](body, parts)
