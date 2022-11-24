from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.transport import RequestsTransport
from roulier.exception import CarrierError

import logging

log = logging.getLogger(__name__)


class ChronopostFrRequestsTransport(RequestsTransport):
    def before_ws_call_transform_payload(self, payload):
        soap_message = self.soap_wrap(payload["body"])
        return soap_message

    def soap_wrap(self, body):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "carriers/chronopost_fr/templates"),
        )

        template = env.get_template("chronopost_soap.xml")
        data = template.render(body=body)
        return data.encode("utf8")

    def _get_requests_headers(self, payload=None):
        return {"content-type": "text/xml"}

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning("Chronopost error 500")
        obj = objectify.fromstring(response.content)
        errors = [
            {
                "id": obj.xpath("//faultcode")[0],
                "message": obj.xpath("//faultstring")[0],
            }
        ]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """Handle response type 200 (success)."""

        def extract_soap(response_xml):
            obj = objectify.fromstring(response_xml)
            return obj.Body.getchildren()[0]

        body = extract_soap(response.content)
        result = body.getchildren()[0]
        if result.errorCode != 0:
            raise CarrierError(response, result.errorMessage)
        body_xml = etree.tostring(body)
        return {"body": body_xml, "response": response}
