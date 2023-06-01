from roulier.codec import DecoderGetLabel
import base64


class KuehneNagelFrDecoderGetLabel(DecoderGetLabel):
    def decode(self, response, payload):
        resp_payload = response["payload"]
        for label_data in resp_payload["labels"]:
            label = {
                "id": label_data["number"],
                "reference": label_data["ref"],
                "tracking": {
                    "number": resp_payload["trackingNumber"],
                    "url": resp_payload.get("trackingUrl", ""),
                    "partner": "",
                },
                "label": {
                    "data": base64.b64encode(label_data["zpl"].encode()),
                    "name": label_data["ref"],
                    "type": "zpl",
                },
            }
            self.result["parcels"].append(label)
