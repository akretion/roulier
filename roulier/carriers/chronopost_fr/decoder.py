from lxml import objectify
from ...codec import DecoderGetLabel
from .api import CHRONOPOST_LABEL_FORMAT


class ChronopostFrDecoder(DecoderGetLabel):
    """Chronopost XML -> Python."""

    def decode(self, response, input_payload):
        """Chronopost XML -> Python."""
        body = response["body"]
        xml = objectify.fromstring(body)

        # Understand a CreateShipmentWithLabelsResponse
        result = xml.getchildren()[0]
        tracking_ref = result.skybillNumber.text
        data = result.skybill.text.encode()
        output_format = input_payload["output_format"]
        parcel = {
            "id": 1,  # no multi parcel management for now.
            "reference": self._get_parcel_number(input_payload),
            "tracking": {"number": tracking_ref, "url": ""},
            "label": {
                "data": data,
                "name": "label_%s" % tracking_ref,
                "type": CHRONOPOST_LABEL_FORMAT.get(output_format, output_format),
            },
        }
        self.result["parcels"].append(parcel)
