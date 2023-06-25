"""Implement laposteWS."""
import json
import logging

from jinja2 import Environment, PackageLoader
from lxml import etree, objectify
from roulier.exception import CarrierError
from roulier.transport import RequestsTransport
from roulier.ws_tools import get_parts, remove_empty_tags

log = logging.getLogger(__name__)


class LaposteFrTransport(RequestsTransport):
    """Implement Laposte WS communication."""

    def before_ws_call_transform_payload(self, payload):
        body = payload["body"]
        headers = payload["headers"]
        soap_message = self.soap_wrap(body, headers)
        return soap_message

    def soap_wrap(self, body, headers):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "carriers/laposte_fr/templates"),
        )

        template = env.get_template("laposte_soap.xml")
        body_stripped = remove_empty_tags(body)
        data = template.render(body=body_stripped)
        return data.encode("utf8")

    def _get_requests_headers(self, payload=None):
        return {"content-type": "text/xml;charset=UTF-8"}

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning("Laposte error 500")
        obj = objectify.fromstring(response.text)
        errors = [
            {
                "id": obj.xpath("//faultcode")[0],
                "message": obj.xpath("//faultstring")[0],
            }
        ]
        raise CarrierError(response, errors)

    def handle_200(self, response):
        """
        Handle response type 200 (success).

        It still can be a success or a failure.
        """

        def raise_on_error(response_xml):
            xml = objectify.fromstring(response_xml)
            messages = xml.xpath("//messages")
            errors = [
                {
                    "id": message.id,
                    "message": str(message.messageContent),
                }
                for message in messages
                if message.type == "ERROR"
            ]
            if len(errors) > 0:
                raise CarrierError(response, errors)

        def extract_xml(response):
            """Because the answer is mixedpart we need to extract."""
            content_type = response.headers["Content-Type"]
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
            "body": extract_body(response_xml),
            "parts": get_parts(response),
            "response": response,
        }


class LaposteFrParcelDocumentTransport(RequestsTransport):
    """Implement laposte Document communication."""

    def __init__(self, config_object):
        super().__init__(config_object)
        self.current_action = config_object.current_action

    def before_ws_call_transform_payload(self, payload):
        if self.current_action.startswith("get_"):
            return json.dumps(payload["body"])
        return payload["body"]

    def _get_requests_headers(self, payload=None):
        headers = payload.get("headers") or {}
        if self.current_action.startswith("get_"):
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "multipart/form-data"
        return headers

    def _get_requests_files(self, payload=None):
        return payload.get("files") or None

    def _get_requests_url(self, payload=None):
        url = super()._get_requests_url(payload)
        if not url.endswith("/"):
            url += "/"
        if self.current_action.startswith("get_"):
            path = self.current_action[4:]
        elif self.current_action == "create_document":
            path = "storedocument"
        elif self.current_action == "update_document":
            path = "updatedocument"
        return url + path

    def _handle_errors(self, response):
        """Handle reponse in case of ERROR 400 type."""
        try:
            laposte_errors = response.json()["errors"]
        except:
            errors = []
        else:
            errors = [
                {
                    "id": e.get("code") or "unkown_%d" % response.status_code,
                    "message": e.get("message") or response.reason,
                }
                for e in laposte_errors
            ]
        if not errors:
            errors.append(
                {
                    "id": "unspecified_%d" % response.status_code,
                    "message": response.reason,
                }
            )
        raise CarrierError(response, errors)

    def _handle_success(self, response):
        if self.current_action == "get_document":
            body = response.content
        else:
            body = response.json()
        return {
            "body": body,
            "response": response,
        }

    def handle_2XX(self, response):
        """
        wrapper to success handler for all 2XX response
        """
        return self._handle_success(response)

    def handle_200(self, response):
        """
        wrapper to success handler for specific 200 response
        (required because abstract in parent)
        """
        return self._handle_success(response)

    def handle_4XX(self, response):
        """
        wrapper to success handler for all 4XX error response
        """
        return self._handle_errors(response)

    def handle_500(self, response):
        """
        wrapper to error handler for specific 500 response
        (required because abstract in parent)
        """
        return self._handle_errors(response)

    def handle_5XX(self, response):
        """
        wrapper to success handler for all 5XX error response
        """
        return self._handle_errors(response)
