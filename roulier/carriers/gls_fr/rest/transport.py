""" Implement GLS WS transport via REST solution"""

from jinja2 import Environment, PackageLoader
import json
import logging
from lxml import objectify, etree

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport
from roulier.ws_tools import remove_empty_tags
from roulier.ws_tools import get_parts

log = logging.getLogger(__name__)


class GlsEuTransport(RequestsTransport):
    """Implement GLS EU communication."""

    def before_ws_call_transform_payload(self, payload):
        return json.dumps(payload["body"])

    def _get_requests_headers(self, payload=None):
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": payload.pop("language", "en") if payload else "en",
        }

    def _get_requests_auth(self, payload):
        return (payload["auth"]["login"], payload["auth"]["password"])

    def _better_error_message(self, message, id=None):
        if id == "0004":
            message = message.replace("An error occurred when validating input: ", "")
        return message

    def _handle_errors(self, response):
        """Handle reponse in case of ERROR 400 type."""
        try:
            gls_errors = response.json()["errors"]
        except:
            errors = []
        else:
            errors = [
                {
                    "id": e.get("exitCode") or "unkown_%d" % response.status_code,
                    "message": self._better_error_message(
                        e.get("description") or e.get("exitMessage") or response.reason,
                        e.get("exitCode"),
                    ),
                }
                for e in gls_errors
            ]
        if not errors:
            errors.append(
                {
                    "id": "unspecified_%d" % response.status_code,
                    "message": self._better_error_message(response.reason),
                }
            )
        raise CarrierError(response, errors)

    def _handle_success(self, response):
        return {
            "body": response.json(),
            "response": response,
        }

    def handle_2XX(self, response):
        """
        wrapper to success handler for all 2XX response
        """
        return self._handle_success(response)

    def handle_200(self, response):
        """
        wrapper to success handler for specific 200 response
        (required because abstract in parent)
        """
        return self._handle_success(response)

    def handle_4XX(self, response):
        """
        wrapper to success handler for all 4XX error response
        """
        return self._handle_errors(response)

    def handle_500(self, response):
        """
        wrapper to error handler for specific 500 response
        (required because abstract in parent)
        """
        return self._handle_errors(response)

    def handle_5XX(self, response):
        """
        wrapper to success handler for all 5XX error response
        """
        return self._handle_errors(response)
