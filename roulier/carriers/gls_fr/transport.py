""" Implement Gls WS transport"""

import requests
from roulier.transport import Transport
from roulier.exception import CarrierError
import logging

log = logging.getLogger(__name__)

WEB_SERVICE_CODING = 'ISO-8859-1'
URL = "http://www.gls-france.com/cgi-bin/glsboxGI%s.cgi"


class GlsTransport(Transport):
    """Implement Gls WS communication."""

    def send(self, payload):
        """Call this function.

        Args:
            payload: input in carrier format
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
                parts: dict of attachments
            }
        """
        response = self.send_request(payload)
        return self.handle_response(response)

    def send_request(self, payload):
        """Send body to Gls WS."""
        ws_url = URL % ""
        if payload.get('isTest'):
            ws_url = URL % "Test"
        headers = {
            'content-type': 'text/plain;charset=%s' % WEB_SERVICE_CODING}
        return requests.post(ws_url, headers=headers, data=payload.get('data'))

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning('Gls error 500')
        errors = [{
        }]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """

        def extract_response_string(response):
            """Because the answer is mixedpart we need to extract."""
            return response._content.decode('ISO-8859-1')

        return {
            'body': extract_response_string(response),
        }

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 200:
            return self.handle_200(response)
        elif response.status_code == 500:
            return self.handle_500(response)  # will raise
        else:
            raise CarrierError(response, [{
                'id': None,
                'message': "Unexpected status code from server",
            }])
