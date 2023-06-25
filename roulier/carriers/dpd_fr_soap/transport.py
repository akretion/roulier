"""Implement dpdWS."""

from jinja2 import Environment, PackageLoader
from lxml import objectify, etree

from roulier.exception import CarrierError
from roulier.transport import RequestsTransport
from roulier.ws_tools import remove_empty_tags

import logging

log = logging.getLogger(__name__)


class DpdTransport(RequestsTransport):
    """Implement Dpd WS communication."""

    def before_ws_call_transform_payload(self, payload):
        body = payload["body"]
        headers = payload["headers"]
        soap_message = self.soap_wrap(body, headers)
        log.debug(soap_message)
        return soap_message

    def soap_wrap(self, body, auth):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "carriers/dpd_fr_soap/templates"),
        )

        template = env.get_template("dpd_soap.xml")
        body_stripped = remove_empty_tags(body)
        header_template = env.get_template("dpd_header.xml")
        header_xml = header_template.render(auth=auth)
        data = template.render(body=body_stripped, header=header_xml)
        return data.encode("utf8")

    def _get_requests_headers(self, payload=None):
        """Send body to dpd WS."""
        return {"content-type": "text/xml"}

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning("Dpd error 500")
        obj = objectify.fromstring(response.content)
        error_id = (obj.xpath("//ErrorId") or obj.xpath("//faultcode"))[0]
        error_message = (obj.xpath("//ErrorMessage") or obj.xpath("//faultstring"))[0]
        raise CarrierError(
            response,
            [
                {
                    "id": error_id,
                    "message": error_message,
                }
            ],
        )

    def handle_200(self, response):
        """Handle response type 200 (success)."""

        def extract_soap(response_xml):
            obj = objectify.fromstring(response_xml)
            return obj.Body.getchildren()[0]

        body = extract_soap(response.content)
        body_xml = etree.tostring(body)
        return {
            "body": body_xml,
            "response": response,
        }
