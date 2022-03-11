# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from roulier.codec import Decoder
from .geodis_common_ws import GEODIS_INFOS


class GeodisDecoderWs(Decoder):
    """Geodis XML -> Python."""

    def decode(self, body, parts, infos):
        """Geodis XML -> Python."""

        def reponse_impression_etiquette(msg, parts):
            output_format = infos["output_format"]
            split_char = '^XZ\r\n^XA' in parts and '^XZ\r\n^XA' or '^XZ\n^XA'
            labels = '^XZ•^XA'.join(parts.split(split_char)).split('•')
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

        def response_find_localite(msg, parts):
            return [{
                "ordre": localite.numOrdre,
                "region": localite.codeRegion,
                "zip": localite.codePostal,
                "city": localite.libelle,
            } for localite in msg.infoLocalite]

        tag = body.tag
        lookup = {
            "{http://impression.service.web.etiquette.geodis.com}reponseImpressionEtiquette":
                reponse_impression_etiquette,
            "{http://localite.service.web.etiquette.geodis.com}findLocaliteResponse":
                response_find_localite,
        }
        return lookup[tag](body, parts)
