"""Implement UPS WS."""

from jinja2 import Environment, PackageLoader
from lxml import objectify, etree

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport
from roulier.ws_tools import remove_empty_tags

import logging
import json

log = logging.getLogger(__name__)


class UpsTransport(RequestsTransport):
    """Implement UPS WS communication."""

    def before_ws_call_transform_payload(self, payload):
        return json.dumps(payload.get("body"))

    def _get_requests_headers(self, payload=None):
        return payload.get("headers")

    def handle_200(self, response):
        """Handle response type 200 (success)."""
        return response.json()

    def handle_500(self, response):
        resp = response.json()
        if resp.get("response", {}).get("errors"):
            raise CarrierError(response, resp.get("response", {}).get("errors"))
        raise CarrierError(response, resp)

    def handle_400(self, response):
        resp = response.json()
        if resp.get("response", {}).get("errors"):
            raise CarrierError(response, resp.get("response", {}).get("errors"))
        raise CarrierError(response, resp)
