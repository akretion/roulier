""" Implement Gls WS transport"""

import logging
import requests

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport


log = logging.getLogger(__name__)

WEB_SERVICE_CODING = "ISO-8859-1"
URL = "http://www.gls-france.com/cgi-bin/glsboxGI%s.cgi"


class GlsTransport(RequestsTransport):
    """Implement Gls WS communication."""

    def _get_requests_headers(self, payload=None):
        return {
            "content-type": "text/plain;charset=%s" % self.config.web_service_coding
        }

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning("Gls error 500")
        errors = [{}]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """

        def extract_response_string(response):
            """Because the answer is mixedpart we need to extract."""
            return response._content.decode("ISO-8859-1")

        return {"body": extract_response_string(response)}

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 200:
            return self.handle_200(response)
        elif response.status_code == 500:
            return self.handle_500(response)  # will raise
        else:
            raise CarrierError(
                response,
                [{"id": None, "message": "Unexpected status code from server"}],
            )
