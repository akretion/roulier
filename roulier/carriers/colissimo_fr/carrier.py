# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import base64
import json
import requests
from requests_toolbelt import MultipartDecoder
from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import (
    ColissimoFrLabelInput,
    ColissimoFrLabelOutput,
    ColissimoFrPackingSlipInput,
    ColissimoFrPackingSlipOutput,
    ColissimoFrGetDocumentsInput,
    ColissimoFrGetDocumentInput,
    ColissimoFrCreateUpdateDocumentInput,
    ColissimoFrDocumentOutput,
    ColissimoFrDocumentsOutput,
    ColissimoFrCreateUpdateDocumentOutput,
)


_logger = logging.getLogger(__name__)


def int_maybe(value):
    try:
        return int(value)
    except ValueError:
        return value


class ColissimoFr(Carrier):
    __key__ = "colissimo_fr"
    __url__ = "https://ws.colissimo.fr/sls-ws/SlsServiceWSRest/2.0"
    __doc_url__ = "https://ws.colissimo.fr/api-document/rest"
    __auth_url__ = "https://ws.colissimo.fr/widget-colissimo/rest"
    __ref__ = "https://www.colissimo.fr/doc-colissimo/redoc-sls/en"

    def _raise_for_status(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                json = response.json()
                if "error" in json:
                    msg = [{"id": 0, "message": json["error"]}]
                elif "errors" in json:
                    msg = [
                        {
                            "id": int_maybe(error.get("code", 0)),
                            "message": error["message"],
                        }
                        for error in json["errors"]
                    ]
                elif "messages" in json:
                    msg = [
                        {
                            "id": int_maybe(error["id"]),
                            "message": error["messageContent"],
                        }
                        for error in json["messages"]
                        if error["type"] == "ERROR"
                    ]
                elif "errorCode" in json and json["errorCode"] != "000":
                    msg = [
                        {
                            "id": int_maybe(json["errorCode"]),
                            "message": json["errorLabel"],
                        }
                    ]
                else:
                    raise
            except Exception:
                msg = response.text

            raise CarrierError(response, msg) from e

        return response

    def _raise_for_error_code(self, response):
        if "errorCode" in response and response["errorCode"] != "000":
            raise CarrierError(
                response,
                [
                    {
                        "id": int_maybe(response["errorCode"]),
                        "message": response["errorLabel"],
                    }
                ],
            )

    def request(self, method, json, url=None):
        headers = {}
        if json and "apiKey" in json:
            json = json.copy()
            headers["apiKey"] = json.pop("apiKey")

        response = requests.post(
            f"{url or self.__url__}/{method}", json=json, headers=headers
        )
        self._raise_for_status(response)
        return response

    def doc_request(self, method, json, files=None):
        kwargs = {}
        if files:
            kwargs["headers"] = json.pop("credential")
            kwargs["data"] = json
            kwargs["files"] = files
        else:
            kwargs["json"] = json

        response = requests.post(f"{self.__doc_url__}/{method}", **kwargs)
        self._raise_for_status(response)
        return response

    def validate(self, params):
        response = self.request("checkGenerateLabel", params)
        _logger.debug("Validation response: %s", response.text)
        return response.text

    def _parse_response(self, response):
        parsed = {}
        decoder = MultipartDecoder.from_response(response)
        for part in decoder.parts:
            content_id = part.headers.get(b"Content-ID", b"").decode("utf-8")
            content_type = part.headers.get(b"Content-Type", b"").decode("utf-8")

            content = part.content

            # Process each part based on its content type
            if "application/json" in content_type:
                parsed[content_id] = json.loads(content.decode("utf-8"))
            elif (
                "application/pdf" in content_type
                or "application/octet-stream" in content_type
            ):
                parsed[content_id] = content
            else:
                _logger.warning(
                    "Unknown content type: %s for id : %s", content_type, content_id
                )
        return parsed

    @action
    def get_label(self, input: ColissimoFrLabelInput) -> ColissimoFrLabelOutput:
        params = input.params()
        self.validate(params)
        response = self.request("generateLabel", params)

        result = self._parse_response(response)
        return ColissimoFrLabelOutput.from_params(result, input)

    @action
    def get_packing_slip(
        self, input: ColissimoFrPackingSlipInput
    ) -> ColissimoFrPackingSlipOutput:

        params = input.params()

        if input.packing_slip_number:
            raise NotImplementedError(
                "Fetching packing slip by number does not seem to "
                "be supported by the REST API"
            )
            # Getting the auth token
            params["login"] = params.pop("contractNumber")
            response = self.request("authenticate.rest", params, url=self.__auth_url__)
            self._raise_for_status(response)
            response = response.json()
            headers = {"token": response["token"]}
            # partnerClientCode
            response = requests.get(
                f"{self.__url__}/SlsInternalService/getBordereauByNumber/{input.packing_slip_number}",
                headers=headers,
            )
            self._raise_for_status(response)
            result = self._parse_response(response)
        else:
            response = self.request("generateBordereauByParcelsNumbers", params)
            result = self._parse_response(response)

        return ColissimoFrPackingSlipOutput.from_params(result)

    @action
    def get_documents(
        self, input: ColissimoFrGetDocumentsInput
    ) -> ColissimoFrDocumentsOutput:
        params = input.params()
        response = self.doc_request("documents", params)
        result = response.json()
        self._raise_for_error_code(result)
        return ColissimoFrDocumentsOutput.from_params(result)

    @action
    def get_document(
        self, input: ColissimoFrGetDocumentInput
    ) -> ColissimoFrDocumentOutput:
        params = input.params()
        response = self.doc_request("document", params)
        return ColissimoFrDocumentOutput.from_params(response.content)

    @action
    def create_document(
        self, input: ColissimoFrCreateUpdateDocumentInput
    ) -> ColissimoFrCreateUpdateDocumentOutput:
        params = input.params()

        with open(input.service.document_path, "rb") as file:
            files = {"file": (params["filename"], file.read())}

        response = self.doc_request("storedocument", params, files)
        result = response.json()
        return ColissimoFrCreateUpdateDocumentOutput.from_params(result)

    @action
    def update_document(
        self, input: ColissimoFrCreateUpdateDocumentInput
    ) -> ColissimoFrCreateUpdateDocumentOutput:
        params = input.params()

        with open(input.service.document_path, "rb") as file:
            files = {"file": (params["filename"], file.read())}

        response = self.doc_request("updatedocument", params, files)
        result = response.json()
        return ColissimoFrCreateUpdateDocumentOutput.from_params(result)
