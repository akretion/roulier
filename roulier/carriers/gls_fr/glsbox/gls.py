""" Implementation for GLS """

from roulier.carrier import Carrier

from .encoder import GlsEncoder
from .decoder import GlsDecoder
from .transport import GlsTransport


class Gls(Carrier):
    """Implementation for GLS"""

    encoder = GlsEncoder()
    decoder = GlsDecoder()
    ws = GlsTransport()

    def api(self):
        """Expose how to communicate with GLS"""
        return self.encoder.api()

    def get(self, data, action=None):
        """Run an action with data against Gls WS"""
        if not action:
            action = "label"
        request = self.encoder.encode(data, action)
        response = self.ws.send(request)
        if isinstance(response, dict):
            response["data_request"] = data
        if action == "label":
            dict_response = self.decoder.decode(response)
            dict_response.update(
                # We also return formatted call and formatted answer
                # for traceability
                {"request_string": request, "response_string": response["body"]}
            )
            return dict_response
        return NotImplementedError

    # shortcuts
    def get_label(self, data):
        """Generate a label"""
        return self.get(data, "label")
