"""Mondial Relay Connect transport: POST an XML body over HTTPS."""

import logging

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport

log = logging.getLogger(__name__)


class MondialRelayConnectTransport(RequestsTransport):
    """Send the XML request to the Connect REST endpoint.

    Authentication is carried inside the XML <Context> (Login/Password/CustomerId),
    not via HTTP headers.
    """

    def before_ws_call_transform_payload(self, payload):
        return payload["body"]

    def _get_requests_headers(self, payload=None):
        return {
            "Content-Type": "text/xml; charset=utf-8",
            "Accept": "application/xml",
        }

    def _handle_response(self, response):
        # Mondial Relay returns 200 even for business errors (carried as <Status>
        # nodes inside the body), so success/failure is decided by the decoder.
        # Keep the raw bytes: the response may be declared as UTF-16.
        return {"body": response.content, "response": response}

    def handle_200(self, response):
        return self._handle_response(response)

    def handle_2XX(self, response):
        return self._handle_response(response)

    def _handle_error(self, response):
        raise CarrierError(
            response,
            [
                {
                    "id": "http_%d" % response.status_code,
                    "message": "Mondial Relay Connect HTTP error %d: %s"
                    % (response.status_code, response.reason),
                }
            ],
        )

    def handle_500(self, response):
        return self._handle_error(response)

    def handle_4XX(self, response):
        return self._handle_error(response)

    def handle_5XX(self, response):
        return self._handle_error(response)
