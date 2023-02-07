"""Implement mondialRelayWS."""
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.carriers.mondialrelay.statuses import STATUSES
from roulier.ws_tools import remove_empty_tags, get_parts
from roulier.exception import CarrierError
import logging

from roulier.transport import RequestsTransport

log = logging.getLogger(__name__)


class MondialRelayTransport(RequestsTransport):
    """Implement MondialRelay WS communication."""

    def before_ws_call_transform_payload(self, payload):
        body = payload["body"]
        headers = payload["headers"]
        soap_message = self.soap_wrap(body, headers)
        return soap_message

    def soap_wrap(self, body, headers):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "carriers/mondialrelay/templates"),
            extensions=["jinja2.ext.with_"],
        )

        template = env.get_template("mondial_relay_soap.xml")
        body_stripped = remove_empty_tags(body)
        data = template.render(body=body_stripped)
        return data.encode("utf8")

    def _get_requests_headers(self, payload=None):
        return {"content-type": "text/xml;charset=UTF-8"}

    def _extract_errors(self, content):
        xml = objectify.fromstring(content)
        statuses = xml.xpath(
            "//mr:STAT",
            namespaces={"mr": "http://www.mondialrelay.fr/webservice/"},
        )
        return [
            {
                "id": status,
                "message": STATUSES[status],
            }
            for status in statuses
            if status
        ]

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        # 500 is not documented, does it even happen?
        log.warning("MondialRelay error 500")

        raise CarrierError(response, self._extract_errors(response.content))

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """

        def extract_body(response_xml):
            """Remove soap wrapper."""
            xml = objectify.fromstring(response_xml)
            payload_xml = xml.Body.getchildren()[0]
            return etree.tostring(payload_xml)

        errors = self._extract_errors(response.content)

        if len(errors) > 0:
            raise CarrierError(response, errors)

        return {
            "body": extract_body(response.content),
            "response": response,
        }
