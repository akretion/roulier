# -*- coding: utf-8 -*-
"""Send a request to a carrier and get the result."""
import requests
from .exception import CarrierError
import logging

log = logging.getLogger(__name__)


class Transport(object):
    _carrier_type = ''
    _action = []
    WS_URL = ''

    def before_ws_call_transform_payload(self, payload):
        return payload

    def send(self, payload):
        data = self.before_ws_call_transform_payload(payload)
        log.debug(data)
        response = self.send_request(data)
        log.info("WS response time %s" % response.elapsed.total_seconds())
        return self.handle_response(response)

    def _get_requests_headers(self):
        return {}

    def send_request(self, body):
        """Send body to Chronopost WS."""
        headers = self._get_requests_headers()
        return requests.post(
            self.WS_URL, headers=headers, data=body
        )

    def handle_200(self, response):
        """ 
            Handle response type 200 (success).
            But it still may contain errors from the carrier webservice.
        """
        raise NotImplementedError

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        raise NotImplementedError

    def handle_400(self, response):
        """Handle reponse in case of ERROR 500 type."""
        raise CarrierError(response, 'Error 400 : Carrier webservice is unavailable')

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 200:
            return self.handle_200(response)
        elif response.status_code == 500:
            log.warning("%s error 500" % self._carrier_type)
            return self.handle_500(response)
        elif response.status_code == 400:
            return self.handle_400(response)
        else:
            raise CarrierError(
                response,
                [
                    {
                        "id": None,
                        "message": "Unexpected status code from server",
                    }
                ],
            )
