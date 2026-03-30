# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import re

import requests
from lxml.etree import fromstring

from ...carrier import Carrier, action
from ...exception import CarrierError
from ...helpers import expand_multi_parcels, factorize_multi_parcels
from .schema import CiblexLabelInput, CiblexLabelOutput

_logger = logging.getLogger(__name__)


class Ciblex(Carrier):
    __key__ = "ciblex"
    __url__ = "https://secure.extranet.ciblex.fr/extranet/client/label.php"
    __url_test__ = "https://secure.extranet.ciblex.fr/extranet/test/label.php"

    def _get_url(self, is_test):
        return self.__url_test__ if is_test else self.__url__

    def _raise_for_status(self, response, type):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                self._parse_response(response, type)
                raise
            except Exception:
                msg = response.text

            raise CarrierError(response, msg) from e

        return response

    def request(self, url, params, type):
        response = requests.get(
            url,
            params=params,
            headers={"Accept": "application/xml"},
            timeout=10,
        )
        self._raise_for_status(response, type)
        return response

    def _parse_response(self, response, format):
        if response.headers.get("Content-Type", "").startswith("application/pdf"):
            label = base64.b64encode(response.content).decode("utf-8")
            tracking = (
                response.headers.get("Content-Disposition", "")
                .split("filename=")[-1]
                .strip('"')
                .split("_")[0]
            )
        elif "/xml" in response.headers.get("Content-Type", ""):
            labels = fromstring(response.content)
            if len(labels) == 0:
                raise CarrierError(response, "No label in response")
            if labels.find("errors") is not None:
                errors = [
                    {"id": error.find("id").text, "message": error.find("message").text}
                    for error in labels.find("errors")
                ]
                raise CarrierError(response, errors)
            label_ = labels.find("label")
            label = label_.find(format.lower())
            tracking = label_.find("cb")
            label = (
                base64.b64encode(label.text.encode("utf-8")).decode("utf-8")
                if label is not None
                else None
            )
            tracking = tracking.text if tracking is not None else None
        else:
            raise CarrierError(
                response,
                "Unsupported content type: %s" % response.headers.get("Content-Type"),
            )

        return [
            {
                "label": label,
                "tracking": tracking,
            }
        ]

    @action
    def get_label(self, input: CiblexLabelInput) -> CiblexLabelOutput:
        url = self._get_url(input.auth.isTest)
        results = []

        for input_mono_parcel in expand_multi_parcels(input):
            params = input_mono_parcel.params()
            type = input_mono_parcel.service.labelFormat.value
            response = self.request(url, params, type)

            result = self._parse_response(response, type)
            results.append(CiblexLabelOutput.from_params(result, input_mono_parcel))

        return factorize_multi_parcels(results)
