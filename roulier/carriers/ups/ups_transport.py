# -*- coding: utf-8 -*-
"""Implement Ups WS."""
import requests
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags
from roulier.exception import CarrierError

import logging

log = logging.getLogger(__name__)


class UpsTransport(Transport):
    """Implement Ups WS communication."""

    UPS_SHIPPING_WS = "https://onlinetools.ups.com/ship/v1807/shipments"
    UPS_SHIPPING_TEST_WS = "https://wwwcie.ups.com/ship/v1807/shipments"

    def send(self, payload, header):
        is_test = header.pop("is_test", None)
        if is_test:
            url = self.UPS_SHIPPING_TEST_WS
        else:
            url = self.UPS_SHIPPING_WS
        response = requests.post(url, json=payload, headers=header)
        return self.handle_response(response)

    def handle_response(self, response):
        """Handle response of webservice."""
        resp = response.json()
        if resp.get("response", {}).get("errors"):
            raise CarrierError(response, resp.get("response", {}).get("errors"))
        if response.status_code != 200:
            raise CarrierError(response, response.text)
        return resp
