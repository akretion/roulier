# -*- coding: utf-8 -*-
"""Implement laposteWS."""
import requests
import email.parser
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags, get_parts
from roulier.exception import CarrierError
import logging

log = logging.getLogger(__name__)


class LaposteTransport(Transport):
    """Implement Laposte WS communication."""

    LAPOSTE_WS = "https://ws.colissimo.fr/sls-ws/SlsServiceWS"

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.header : auth
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
                parts: dict of attachments
            }
        """
        body = payload['body']
        headers = payload['headers']
        soap_message = self.soap_wrap(body, headers)
        log.debug(soap_message)
        response = self.send_request(soap_message)
        return self.handle_response(response)

    def soap_wrap(self, body, headers):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/laposte/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("laposte_soap.xml")
        body_stripped = remove_empty_tags(body)
        data = template.render(body=body_stripped)
        return data.encode('utf8')

    def send_request(self, body):
        """Send body to laposte WS."""
        return requests.post(
            self.LAPOSTE_WS,
            headers={'content-type': 'text/xml;charset=UTF-8'},
            data=body)

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
                    'message': unicode(message.messageContent),
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

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 200:
            return self.handle_200(response)
        elif response.status_code == 500:
            return self.handle_500(response)  # will raise
        else:
            raise CarrierError(response, [{
                'id': None,
                'message': "Unexpected status code from server",
            }])

    