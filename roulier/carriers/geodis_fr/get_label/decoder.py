"""Geodis XML -> Python."""
from roulier.codec import DecoderGetLabel
import base64


class GeodisFrParcelDecoder(DecoderGetLabel):
    """Geodis XML -> Python."""

    def decode(self, response, input_payload):
        """Chronopost XML -> Python."""
        body = response["body"]
        parts = response["parts"].decode()
        output_format = self.config.roulier_input.get("service", {}).get("labelFormat")
        extension = self.config.label_formats.get(output_format)[1]
        labels = parts.replace("\r\n", "\n")
        labels = "^XZ•^XA".join(labels.split("^XZ\n^XA")).split("•")
        labels_idx = iter(range(len(labels)))
        labels_data = iter(labels)
        for colis in body.infoColis:
            codeUmg = getattr(colis, "codumg", "") and colis.codumg.text or ""
            numero = getattr(colis, "numero", "") and colis.numero.text or ""
            cabclt = getattr(colis, "cabclt", "") and colis.cabclt.text or ""
            cab = getattr(colis, "cab", "") and colis.cab.text or ""
            tracking = body.cabRouting.text or ""
            parcel = {
                "codeUmg": codeUmg,
                "id": numero,
                "reference": cabclt,
                "number": cab,
                "tracking": {"number": "", "url": ""},
                "label": {
                    "data": base64.b64encode(next(labels_data).encode()),
                    "name": cabclt or cab or numero or "label_%s" % next(labels_idx),
                    "type": extension,
                },
            }
            self.result["parcels"].append(parcel)
        self.result["extra"] = (
            {
                "reseau": getattr(body, "reseau", "") and body.reseau.text or "",
                "priorite": getattr(body, "priorite", "") and body.priorite.text or "",
                "codeDirectionel": getattr(body, "codire", "")
                and body.codire.text
                or "",
                "cabRouting": getattr(body, "cabRouting", "")
                and body.cabRouting.text
                or "",
            },
        )
