# -*- coding: utf-8 -*-
"""Implement geodisWS."""
import requests

from roulier.transport import Transport
from roulier.exception import CarrierError
import json
import logging
import hashlib
import time

log = logging.getLogger(__name__)


class GeodisTransportRestWs(Transport):
    """Implement Geodis Rest WS communication."""

    def get_token(self, id, timestamp, lang, hash):
        params = [id, timestamp, lang, hash]
        return ';'.join(params)

    def get_hash(self, api_key, id, timestamp, lang, service, json_data):
        return hashlib.sha256(
            ";".join([
                api_key, id, timestamp, lang, service,
                json_data
            ]).encode("utf-8")
        ).hexdigest()

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: JSON
            payload.header : auth
            payload.infos: { url: string, xmlns: string}
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
                parts: empty dict // compat with WS
            }
        """
        timestamp = "%d" % (time.time() * 1000)
        lang = "fr"
        login = payload['headers']['login']
        api_key = payload['headers']['password']
        body = json.dumps(payload['body'])
        service = payload['infos']['service']
        hash = self.get_hash(api_key, login, timestamp, lang, service, body)
        token = self.get_token(login, timestamp, lang, hash)
        infos = payload['infos']
        infos['token'] = token
        response = self.send_request(body, infos)
        log.info('WS response time %s' % response.elapsed.total_seconds())
        return self.handle_response(response)

    def send_request(self, body, infos):
        """Send body to geodis WS."""
        ws_url = infos['url']
        token = infos['token']
        return requests.post(
            ws_url,
            headers={
                'X-GEODIS-Service': token,
            },
            data=body)

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        # TODO : put a try catch (like wrong server)
        log.warning('Geodis error 500')
        errors = [{
            "id": "",
            "message": "",
        }]
        raise CarrierError(response, errors)

    def handle_true_negative_error(self, response):
        """When servers answer an error with a 200 status code."""
        errors = [{
            "id": response.get('codeErreur', ''),
            "message": response.get('texteErreur', '')
        }]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """Handle response type 200."""
        payload = json.loads(response.text)
        if payload['ok'] is not True:
            self.handle_true_negative_error(response)
        return {
            "body": payload.get('contenu', []),
            "parts": [],
            "response": response,
        }

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 500:
            return self.handle_500(response)
        elif response.status_code == 200:
            return self.handle_200(response)
        else:
            raise CarrierError(response, [{
                'id': None,
                'message': "Unexpected status code from server",
            }])
