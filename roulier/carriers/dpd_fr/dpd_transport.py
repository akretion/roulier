# -*- coding: utf-8 -*-
"""Implement dpdWS."""
import requests
import json
import logging

from roulier.transport import Transport
from roulier.exception import CarrierError


log = logging.getLogger(__name__)



class DpdTransport(Transport):
    """Implement Dpd WS communication."""

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: JSON
            payload.auth : auth
            payload.infos: { url: string, xmlns: string}
        Return:
            {
                response: (Requests.response)
                body: dict
                parts: empty dict // compat with WS
            }
        """
        body = payload['body']
        auth = payload['auth']
        infos = payload['infos']

        response = self.send_request(body, auth, infos)
        log.info('WS response time %s' % response.elapsed.total_seconds())
        return self.handle_response(response)


    def send_request(self, body, auth, infos):
        """Send body to dpd WS."""
        ws_url = infos['url']
        return requests.post(
            ws_url,
            auth=(auth['login'], auth['password']),
            json=body)


    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning('Dpd error 500')
        errors = [{
            "id": "",
            "message": "",
        }]
        raise CarrierError(response, errors)

    def handle_true_negative_error(self, response, payload):
        """When servers answer an error with a 200 status code."""
        errors = [{
            "id": payload.get('code', ''),
            "message": payload.get('message', '')
        }]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """Handle response type 200."""
        payload = json.loads(response.text)
        if payload.get('httpStatus', 200) is not 200:
            self.handle_true_negative_error(response, payload)
        return {
            "body": payload,
            "parts": [],
            "response": response,
        }

    def handle_403(self, response):
        """Handle response type 403."""
        raise CarrierError(response,[{
            "id": "",
            "message": "Access Denied.",
        }])


    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 500:
            return self.handle_500(response)
        elif response.status_code == 403:
            return self.handle_403(response)
        elif response.status_code == 200:
            return self.handle_200(response)
        else:
            raise CarrierError(response, [{
                'id': None,
                'message': "Unexpected status code from server",
            }])
