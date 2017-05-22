# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from roulier.codec import Decoder


class GeodisDecoder(Decoder):
    """Geodis XML -> Python."""

    def decode(self, body, parts, output_format):
        """Geodis XML -> Python."""

        def reponse_impression_etiquette(msg, parts):
            labels = '^XZ•^XA'.join(parts.split('^XZ\r\n^XA')).split('•')
            labels_idx = iter(range(len(labels)))
            labels_data = iter(labels)
            return {
                "tracking": {
                    "number": body.cabRouting,
                },
                "label": {
                    "name": "label",
                    "data": parts,
                    "type": output_format
                },
                "parcels": [{
                    "codeUmg": getattr(colis, 'codumg', ''),
                    "id": getattr(colis, 'numero', ''),
                    "number": getattr(colis, 'cab', ''),
                    "reference": getattr(colis, 'cabclt', ''),
                    "label": {
                        "name": "label_%s" % labels_idx.next(),
                        "data": labels_data.next(),
                        "type": output_format,
                    }
                } for colis in body.infoColis],
                "annexes": [
                ],
                "extra": {
                    "reseau": getattr(body, 'reseau', ''),
                    "priorite": getattr(body, 'priorite', ''),
                    "codeDirectionel": getattr(body, 'codire', ''),
                    "cabRouting": getattr(body, 'cabRouting', ''),
                }
            }

        tag = body.tag
        lookup = {
            "{http://impression.service.web.etiquette.geodis.com}reponseImpressionEtiquette":
                reponse_impression_etiquette,
        }
        return lookup[tag](body, parts)
