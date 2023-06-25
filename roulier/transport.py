"""Send a request to a carrier and get the result."""
import logging
import os
import requests
from abc import ABC, abstractmethod
from .exception import CarrierError

log = logging.getLogger(__name__)


class TransportBase(ABC):
    def __init__(self, config_object):
        self.config = config_object


class RequestsTransport(TransportBase, ABC):
    def before_ws_call_prepare_request_kwargs(self, payload):
        return {
            "body": self.before_ws_call_transform_payload(payload),
            "headers": self._get_requests_headers(payload),
            "auth": self._get_requests_auth(payload),
            "url": self._get_requests_url(payload),
            "files": self._get_requests_files(payload),
        }

    def before_ws_call_transform_payload(self, payload):
        return payload

    def send(self, payload):
        request_kwargs = self.before_ws_call_prepare_request_kwargs(payload)
        log.debug(request_kwargs["body"])

        if os.environ.get("ROULIER_PROXY"):
            request_kwargs["proxies"] = {
                "http": os.environ["ROULIER_PROXY"],
                "https": os.environ["ROULIER_PROXY"],
            }

        response = self.send_request(**request_kwargs)
        log.debug("WS response time %s" % response.elapsed.total_seconds())
        return self.handle_response(response)

    def _get_requests_headers(self, payload=None):
        return None

    def _get_requests_files(self, payload=None):
        return None

    def _get_requests_auth(self, payload=None):
        return None

    def _get_requests_url(self, payload=None):
        if self.config.is_test and self.config.ws_test_url:
            return self.config.ws_test_url
        return self.config.ws_url

    def send_request(self, body, url, auth=None, headers=None, method="post", **kwargs):
        send = getattr(requests, method)
        return send(url, headers=headers, auth=auth, data=body, **kwargs)

    @abstractmethod
    def handle_200(self, response):
        """
        Handle response type 200 (success).
        But it still may contain errors from the carrier webservice.
        """
        pass

    @abstractmethod
    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        pass

    def handle_response(self, response):
        """Handle response of webservice."""
        str_status_code = "%s" % response.status_code
        if hasattr(self, "handle_%d" % response.status_code):
            handle = getattr(self, "handle_%d" % response.status_code)
        elif hasattr(self, "handle_%sXX" % str_status_code[0]):
            handle = getattr(self, "handle_%sXX" % str_status_code[0])
        else:
            raise CarrierError(
                response,
                [
                    {
                        "id": None,
                        "message": ("Unexpected status code from server. " "%s: %s")
                        % (response.status_code, response.reason),
                    }
                ],
            )
        if response.status_code < 200 or response.status_code >= 300:
            log.warning(
                "%s error %d" % (self.config.carrier_type, response.status_code)
            )
        return handle(response)
