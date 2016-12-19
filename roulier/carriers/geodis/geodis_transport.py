# -*- coding: utf-8 -*-
"""Implement geodisWS."""
import requests
import email.parser
from lxml import objectify
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags
import logging

log = logging.getLogger(__name__)


class GeodisTransport(Transport):
    """Implement Geodis WS communication."""

    GEODIS_WS = "http://espace.geodis.com/geolabel/services/ImpressionEtiquette"  # nopep8
    GEODIS_WS_TEST = "http://espace.recette.geodis.com/geolabel/services/ImpressionEtiquette"  # nopep8
    STATUS_SUCCES = "success"
    STATUS_ERROR = "error"

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.header : auth
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (lxml)
                response: (Requests.response)
                payload: usefull payload (if success) (xml as string)

            }
        """
        body = payload['body']
        headers = payload['headers']
        is_test = payload['is_test']
        soap_message = self.soap_wrap(body, headers)
        log.debug(soap_message)
        response = self.send_request(soap_message, is_test)
        log.info('WS response time %s' % response.elapsed.total_seconds())
        return self.handle_response(response)

    def soap_wrap(self, body, auth):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/geodis/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("geodis_soap.xml")
        body_stripped = remove_empty_tags(body)
        header_template = env.get_template("geodis_header.xml")
        header_xml = header_template.render(auth=auth)
        data = template.render(body=body_stripped, header=header_xml)
        return data.encode('utf8')

    def send_request(self, body, is_test):
        """Send body to geodis WS."""
        ws_url = self.GEODIS_WS_TEST if is_test else self.GEODIS_WS
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
        # no need to extract_body shit here
        log.warning('Geodis error 500')
        xml = self.get_parts(response)['start']
        obj = objectify.fromstring(xml)
        message = obj.xpath("//*[local-name() = 'message']")
        if len(message) > 0:
            message = message[0] or obj.xpath('//faultstring')[0]
            id_message = obj.xpath("//*[local-name() = 'code']")[0]
        return {
            "id": obj.xpath('//faultcode')[0],
            "status": self.STATUS_ERROR,
            "messages": [{  # only one error msg is returned by ws
                'id': id_message,
                'message': message,
            }],
            "response": response,
        }

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """
        parts = self.get_parts(response)
        xml = parts['start']

        def extract_soap(response_xml):
            obj = objectify.fromstring(response_xml)
            return obj.Body.getchildren()[0]

        payload = extract_soap(xml)
        attachement_id = payload.codeAttachement.text[4:]  # remove cid:
        attachement = parts[attachement_id]
        # payload.infoColis.cab

        return {
            "status": "ok",
            "message": "",
            "payload": payload,
            "attachement": attachement,
            "response": response,
        }

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 500:
            return self.handle_500(response)
        elif response.status_code == 200:
            return self.handle_200(response)
        else:
            return {
                "status": "error",
                "messages": [{
                    'id': False,
                    'message': "Unexpected status code from server",
                }],
                "response": response
            }

    def get_parts(self, response):
        head_lines = ''
        for k, v in response.raw.getheaders().iteritems():
            head_lines += str(k)+':'+str(v)+'\n'

        full = head_lines + response.content

        parser = email.parser.Parser()
        decoded_reply = parser.parsestr(full)
        parts = {}
        start = decoded_reply.get_param('start').lstrip('<').rstrip('>')
        i = 0
        for part in decoded_reply.get_payload():
            cid = part.get('content-Id', '').lstrip('<').rstrip('>')
            if (not start or start == cid) and 'start' not in parts:
                parts['start'] = part.get_payload()
            else:
                parts[cid or 'Attachment%d' % i] = part.get_payload()
            i += 1

        return parts
