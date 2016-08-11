# -*- coding: utf-8 -*-
"""Implement laposteWS."""
import requests
import email.parser
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags
import logging

log = logging.getLogger(__name__)


class LaposteTransport(Transport):
    """Implement Laposte WS communication."""

    LAPOSTE_WS = "https://ws.colissimo.fr/sls-ws/SlsServiceWS"
    STATUS_SUCCES = "success"
    STATUS_ERROR = "error"

    def send(self, body):
        """Call this function.

        Args:
            body: XML in a string
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (lxml)
                response: (Requests.response)
                payload: usefull payload (if success) (xml as string)

            }
        """
        soap_message = self.soap_wrap(body)
        log.debug(soap_message)
        response = self.send_request(soap_message)
        log.info('WS response time %s' % response.elapsed.total_seconds())
        return self.handle_response(response)

    def soap_wrap(self, body):
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
            headers={'content-type': 'text/xml'},
            data=body)

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        # TODO : put a try catch (like wrong server)
        # no need to extract_body shit here
        log.warning('Laposte error 500')
        obj = objectify.fromstring(response.text)
        return {
            "id": obj.xpath('//faultcode')[0],
            "status": self.STATUS_ERROR,
            "message": obj.xpath('//faultstring')[0],
            "response": response,
            "payload": None
        }

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """
        def extract_message(response_xml):
            xml = objectify.fromstring(response_xml)
            message = xml.xpath('//messages')[0]  # always one
            # dirty serialization
            return {
                "id": message.id,
                "type": message.type,
                "message": message.messageContent
            }

        def extract_payload(response_xml):
            xml = objectify.fromstring(response_xml)
            payload_xml = xml.Body.getchildren()[0]
            return etree.tostring(payload_xml)

        def extract_body(response):
            """Because the answer is mixedpart we need to extract."""
            content_type = response.headers['Content-Type']
            boundary = content_type.split('boundary="')[1].split('";')[0]
            start = content_type.split('start="')[1].split('";')[0]

            between_boundaries = response.text.split("--%s" % boundary)[1]
            after_start = between_boundaries.split(start)[1]
            clean_xml = after_start.strip()  # = trim()
            return clean_xml

        response_xml = extract_body(response)

        message = extract_message(response_xml)

        status = self.STATUS_ERROR
        payload = None

        if message['type'] == "INFOS":
            status = self.STATUS_SUCCES
            payload = extract_payload(response_xml)
        else:
            log.warning('Laposte error 200')
        log.info('status: %s' % status)
        log.debug('message: %s' % message)

        return {
            "status": status,
            "message": message,
            "payload": payload,
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
                "message": "Unexpected status code from server",
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
