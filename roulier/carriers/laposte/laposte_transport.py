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

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.headers: auth
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
        # TODO : put a try catch (like wrong server)
        # no need to extract_body shit here
        log.warning('Laposte error 500')
        obj = objectify.fromstring(response.text)
        exception = {
            "id": obj.xpath('//faultcode')[0],
            "status": self.STATUS_ERROR,
            "message": obj.xpath('//faultstring')[0],
            "response": response,
            "payload": None
        }
        if isinstance(exception['message'], objectify.StringElement):
            exception['messages'] = [unicode(exception['message'])]
        if isinstance(exception['message'], dict) and \
                exception.get('exception'):
            exception['messages'] = self.exception_handling(
                exception['message']['message'])
        return exception

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """
        def extract_message(response_xml):
            xml = objectify.fromstring(response_xml)
            messages = xml.xpath('//messages')
            exception = False
            for message in messages:
                mess_type = str(message.type)
                if mess_type.lower() == self.STATUS_ERROR.lower():
                    exception = True
            # dirty serialization
            return {
                "exception": exception,
                "message": messages,
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

        payload = None

        if message['exception']:
            log.warning('Laposte error 200')
            status = self.STATUS_ERROR
        else:
            status = self.STATUS_SUCCES
            payload = extract_payload(response_xml)
        log.info('status: %s' % status)
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
            head_lines += str(k) + ':' + str(v) + '\n'

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

    def exception_handling(self, messages):
        message_labels = []
        for message in messages:
            if message.messageContent:
                message_labels.append({
                    'id': message.id,
                    'message': unicode(message.messageContent),
                })
        log.debug('message: %s' % message_labels)
        return message_labels
