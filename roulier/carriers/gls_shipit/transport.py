"""Implement GLS WS transport via REST solution"""

from datetime import datetime, timedelta

from jinja2 import Environment, PackageLoader
import json
import logging
from lxml import objectify, etree

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport
from roulier.ws_tools import remove_empty_tags
from roulier.ws_tools import get_parts

log = logging.getLogger(__name__)


class GlsShipItTransport(RequestsTransport):
    """Implement GLS EU communication."""

    def before_ws_call_transform_payload(self, payload):
        return json.dumps(payload["body"])

    def _get_requests_headers(self, payload=None):
        return {
            "Content-Type": "application/glsVersion1+json;charset=UTF-8",
            "Accept": "application/glsVersion1+json, application/json",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": payload.pop("language", "en") if payload else "en",
            "Authorization": "Bearer " + self._get_auth_token(payload),
        }

    def _get_requests_url(self, payload=None) -> str:
        if self.config.is_test and self.config.ws_test_url:
            base_url = self.config.ws_test_url
        else:
            base_url = self.config.ws_url
        return base_url + "/shipit-farm/v1/backend/rs/shipments"

    def _get_auth_token(self, payload) -> str:
        auth_token = getattr(self, "_auth_token", None)
        now = datetime.now()
        if auth_token:
            if auth_token["expires_at"] <= now + timedelta(seconds=10):
                auth_token = None
        if not auth_token:
            if self.config.is_test and self.config.ws_test_url:
                base_url = self.config.ws_test_url
            else:
                base_url = self.config.ws_url
            url = base_url + "/oauth2/v2/token"
            body = {
                "grant_type": "client_credentials",
                "client_id": payload["auth"]["login"],
                "client_secret": payload["auth"]["password"],
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept": "application/json",
                "Accept-Encoding": "gzip,deflate",
            }
            response = self.send_request(
                body, url, method="post", headers=headers, timeout=10
            )
            if not response.ok:
                self._handle_errors(response)
            auth_token = response.json()
            auth_token["expires_at"] = now + timedelta(seconds=auth_token["expires_in"])
            self._auth_token = auth_token
        return self._auth_token["access_token"]

    def _handle_errors(self, response):
        """Handle reponse in case of ERROR 400 type."""
        if "error" in response.headers:
            error_code = response.headers["error"]
            error_message = response.headers.get("message")
            # error_args =  response.headers.get("args")
            raise CarrierError(response, error_message or error_code)
        else:
            try:
                data = response.json()
                errors = " ; ".join(e["message"] for e in data["errors"])
            except:
                pass
            else:
                raise CarrierError(response, errors)
        raise CarrierError(
            response, response.text or f"{response.status_code}: {response.reason}"
        )

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
