# -*- coding: utf-8 -*-
"""Implement laposteWS."""
import requests
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.ws_tools import remove_empty_tags, get_parts
from roulier.exception import CarrierError
import logging

from roulier.transport import Transport
from .common import CARRIER_TYPE, LAPOSTE_WS

log = logging.getLogger(__name__)


class LaposteFrTransport(Transport):
    """Implement Laposte WS communication."""
    _carrier_type = CARRIER_TYPE
    _action = ['get_label']
    WS_URL = LAPOSTE_WS

    def before_ws_call_transform_payload(self, payload):
        body = payload['body']
        headers = payload['headers']
        soap_message = self.soap_wrap(body, headers)
        return soap_message

    def soap_wrap(self, body, headers):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/laposte/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("laposte_soap.xml")
        body_stripped = remove_empty_tags(body)
        data = template.render(body=body_stripped)
        return data.encode('utf8')

    def _get_requests_headers(self):
        return {'content-type': 'text/xml;charset=UTF-8'}

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning('Laposte error 500')
        obj = objectify.fromstring(response.text)
        errors = [{
            "id": obj.xpath('//faultcode')[0],
            "message": obj.xpath('//faultstring')[0],
        }]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """
        def raise_on_error(response_xml):
            xml = objectify.fromstring(response_xml)
            messages = xml.xpath('//messages')
            errors = [
                {
                    'id': message.id,
                    'message': str(message.messageContent),
                }
                for message in messages if message.type == "ERROR"
            ]
            if len(errors) > 0:
                raise CarrierError(response, errors)

        def extract_xml(response):
            """Because the answer is mixedpart we need to extract."""
            content_type = response.headers['Content-Type']
            boundary = content_type.split('boundary="')[1].split('";')[0]
            start = content_type.split('start="')[1].split('";')[0]

            between_boundaries = response.text.split("--%s" % boundary)[1]
            after_start = between_boundaries.split(start)[1]
            clean_xml = after_start.strip()  # = trim()
            return clean_xml

        def extract_body(response_xml):
            """Remove soap wrapper."""
            xml = objectify.fromstring(response_xml)
            payload_xml = xml.Body.getchildren()[0]
            return etree.tostring(payload_xml)

        response_xml = extract_xml(response)
        raise_on_error(response_xml)
        return {
            'body': extract_body(response_xml),
            'parts': get_parts(response),
            'response': response,
        }
