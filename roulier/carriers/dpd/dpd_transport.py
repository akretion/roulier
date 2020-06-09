# -*- coding: utf-8 -*-
"""Implement dpdWS."""
import requests
from lxml import objectify, etree
from jinja2 import Environment, PackageLoader
from roulier.transport import Transport
from roulier.ws_tools import remove_empty_tags
from roulier.exception import CarrierError

import logging

log = logging.getLogger(__name__)


class DpdTransport(Transport):
    """Implement Dpd WS communication."""

    DPD_WS = (
        "https://e-station.cargonet.software/dpd-eprintwebservice/eprintwebservice.asmx"
    )

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.header : auth
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
            }
        """
        body = payload["body"]
        headers = payload["headers"]
        soap_message = self.soap_wrap(body, headers)
        log.debug(soap_message)
        response = self.send_request(soap_message)
        log.info("WS response time %s" % response.elapsed.total_seconds())
        return self.handle_response(response)

    def soap_wrap(self, body, auth):
        """Wrap body in a soap:Enveloppe."""
        env = Environment(
            loader=PackageLoader("roulier", "/carriers/dpd/templates"),
            extensions=["jinja2.ext.with_"],
        )

        template = env.get_template("dpd_soap.xml")
        body_stripped = remove_empty_tags(body)
        header_template = env.get_template("dpd_header.xml")
        header_xml = header_template.render(auth=auth)
        data = template.render(body=body_stripped, header=header_xml)
        return data.encode("utf8")

    def send_request(self, body):
        """Send body to dpd WS."""
        return requests.post(
            self.DPD_WS, headers={"content-type": "text/xml"}, data=body
        )

    def handle_500(self, response):
        """Handle reponse in case of ERROR 500 type."""
        log.warning("Dpd error 500")
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
        body_xml = etree.tostring(body)
        return {
            "body": body_xml,
            "response": response,
        }

    def handle_response(self, response):
        """Handle response of webservice."""
        if response.status_code == 200:
            return self.handle_200(response)
        elif response.status_code == 500:
            return self.handle_500(response)
        else:
            raise CarrierError(
                response,
                [{"id": None, "message": "Unexpected status code from server",}],
            )
