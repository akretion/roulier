# -*- coding: utf-8 -*-
"""Implement geodisWS."""
import requests
from lxml import objectify
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags, get_parts
from roulier.exception import CarrierError
import logging

log = logging.getLogger(__name__)


class GeodisTransportWs(Transport):
    """Implement Geodis WS communication."""

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.header : auth
            payload.infos: { url: string, xmlns: string}
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
                parts: dict of attachments
            }
        """
        body = payload['body']
        headers = payload['headers']
        infos = payload['infos']
        soap_message = self.soap_wrap(body, headers, infos)
        response = self.send_request(soap_message, infos)
        log.info('WS response time %s' % response.elapsed.total_seconds())
        return self.handle_response(response)

    def soap_wrap(self, body, auth, infos):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/geodis/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("geodis_soap.xml")
        body_stripped = remove_empty_tags(body)
        header_template = env.get_template("geodis_header.xml")
        header_xml = header_template.render(auth=auth, xmlns=infos['xmlns'])
        data = template.render(
            body=body_stripped, header=header_xml, xmlns=infos['xmlns'])
        return data.encode('utf8')

    def send_request(self, body, infos):
        """Send body to geodis WS."""
        ws_url = infos['url']
        return requests.post(
            ws_url,
            headers={
                'content-type': 'text/xml',
                'SOAPAction': '<SOAP Action>'
            },
            data=body)

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        # TODO : put a try catch (like wrong server)
        log.warning('Geodis error 500')
        xml = get_parts(response)['start']
        obj = objectify.fromstring(xml)
        message = obj.xpath("//*[local-name() = 'message']")
        id_message = None
        if len(message) > 0:
            message = message[0] or obj.xpath('//faultstring')[0]
            id_message = (
                obj.xpath("//*[local-name() = 'code']") and
                obj.xpath("//*[local-name() = 'code']")[0] or '')
        errors = [{
            "id": id_message,
            "message": message,
        }]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """Handle response type 200."""
        parts = get_parts(response)
        xml = parts['start']

        def extract_soap(response_xml):
            obj = objectify.fromstring(response_xml)
            return obj.Body.getchildren()[0]

        payload = extract_soap(xml)
        try:
            # TODO : may be extract this elsewere
            # rechercheLocalite has no attachment
            attachement_cid = payload.codeAttachement.text[len('cid:'):]
            attachement = parts[attachement_cid]
        except AttributeError:
            attachement = None

        return {
            "body": payload,
            "parts": attachement,
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
