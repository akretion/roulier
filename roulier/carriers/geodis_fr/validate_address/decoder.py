"""Geodis XML -> Python."""
from roulier.codec import DecoderGetLabel


class GeodisFrValidateAddressDecoder(DecoderGetLabel):
    """Geodis XML -> Python."""

    def decode(self, response, input_payload):
        body = response["body"]
        self.result = [
            {
                "ordre": localite.numOrdre,
                "region": localite.codeRegion,
                "zip": localite.codePostal,
                "city": localite.libelle,
            }
            for localite in body.infoLocalite
        ]
