"""Implement geodisWS."""
from lxml import objectify
from jinja2 import Environment, PackageLoader
from roulier.ws_tools import remove_empty_tags, get_parts
from roulier.exception import CarrierError
import logging

from roulier.transport import RequestsTransport

log = logging.getLogger(__name__)


class GeodisFrSoapTransport(RequestsTransport):
    """Implement Geodis WS communication."""

    def before_ws_call_transform_payload(self, payload):
        soap_message = self.soap_wrap(payload)
        return soap_message

    def soap_wrap(self, payload):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "carriers/geodis_fr/templates"),
        )
        body = payload["body"]
        headers = payload["headers"]
        template = env.get_template("geodis_soap.xml")
        body_stripped = remove_empty_tags(body)
        header_template = env.get_template("geodis_header.xml")
        xmlns = self.config.xmlns
        header_xml = header_template.render(auth=headers, xmlns=xmlns)
        data = template.render(body=body_stripped, header=header_xml, xmlns=xmlns)

        return data.encode("utf8")

    def _get_requests_headers(self, payload=None):
        return {"content-type": "text/xml", "SOAPAction": "<SOAP Action>"}

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        # TODO : put a try catch (like wrong server)
        log.warning("Geodis error 500")
        xml = get_parts(response)["start"]
        obj = objectify.fromstring(xml)
        message = obj.xpath("//*[local-name() = 'message']")
        if not message:
            message = obj.xpath("//*[local-name() = 'faultstring']")
        id_message = None
        if len(message) > 0:
            message = message[0] or obj.xpath("//faultstring")[0]
            id_message = (
                obj.xpath("//*[local-name() = 'code']")
                and obj.xpath("//*[local-name() = 'code']")[0]
                or ""
            )
        errors = [
            {
                "id": id_message,
                "message": message,
            }
        ]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """Handle response type 200."""
        parts = get_parts(response)
        xml = parts["start"]

        def extract_soap(response_xml):
            obj = objectify.fromstring(response_xml)
            return obj.Body.getchildren()[0]

        payload = extract_soap(xml)
        try:
            # TODO : may be extract this elsewere
            # rechercheLocalite has no attachment
            attachement_cid = payload.codeAttachement.text[len("cid:") :]
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
            raise CarrierError(
                response,
                [
                    {
                        "id": None,
                        "message": "Unexpected status code from server",
                    }
                ],
            )
