# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import DHLExpressLabelInput, DHLExpressLabelOutput

_logger = logging.getLogger(__name__)


def int_maybe(value):
    try:
        return int(value)
    except ValueError:
        return value


class DHLExpress(Carrier):
    __key__ = "dhl_express"
    __url__ = "https://express.api.dhl.com/mydhlapi"
    __url_test__ = "https://express.api.dhl.com/mydhlapi/test"

    __ref__ = "https://developer.dhl.com/api-reference/mydhl-api-dhl-express"

    def _get_url(self, is_test):
        return self.__url_test__ if is_test else self.__url__

    def _raise_for_status(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                json = response.json()
                if "message" in json:
                    id = 0
                    detail = json.get("detail", "")
                    if detail and ":" in detail and detail.split(":", 1)[0].isdigit():
                        id, detail = detail.split(":", 1)
                        id = int_maybe(id.strip())
                        detail = detail.strip()
                    msg = [
                        {
                            "id": id,
                            "message": f"{json['message']} ({detail})",
                        }
                    ]

                    if "additionalDetails" in json:
                        for additional_detail in json["additionalDetails"]:
                            if (
                                "message" in additional_detail
                                and ":" in additional_detail["message"]
                                and additional_detail["message"]
                                .split(":", 1)[0]
                                .isdigit()
                            ):
                                id, message = additional_detail["message"].split(":", 1)
                                id = int_maybe(id.strip())
                                message = message.strip()
                            else:
                                id = 0
                                message = additional_detail.get("message", "")
                            msg.append(
                                {
                                    "id": id,
                                    "message": message,
                                }
                            )
                else:
                    raise
            except Exception:
                msg = response.text

            raise CarrierError(response, msg) from e

        return response

    def request(self, url, method, json):
        json = json.copy()
        headers = {
            "Accept": "application/json",
            "Authorization": json.pop("authorization"),
            "Content-Type": "application/json",
            "x-version": "3.1.0",
        }
        response = requests.post(f"{url}/{method}", json=json, headers=headers)
        self._raise_for_status(response)
        return response

    def _parse_response(self, response):
        return response.json()

    @action
    def get_label(self, input: DHLExpressLabelInput) -> DHLExpressLabelOutput:
        url = self._get_url(input.auth.isTest)
        params = input.params()
        response = self.request(url, "shipments", params)
        result = self._parse_response(response)
        return DHLExpressLabelOutput.from_params(result, input)
