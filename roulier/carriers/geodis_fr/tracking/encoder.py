"""Implementation of Geodis Api."""
from roulier.codec import Encoder


class GeodisEncoderRestWs(Encoder):
    def transform_input_to_carrier_webservice(self, data):
        return {
            "headers": data["auth"],
            "body": data["service"],
        }
