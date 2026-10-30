# Copyright 2026 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64encode

import requests

from ...carrier import Carrier, action
from ...exception import CarrierError
from ...schema import PickupSiteGetInput
from .schema import (
    SendcloudLabelInput,
    SendcloudLabelOutput,
    SendcloudPickupSiteGetOutput,
    SendcloudPickupSiteSearchInput,
    SendcloudPickupSiteSearchOutput,
)


class Sendcloud(Carrier):
    __key__ = "sendcloud"
    __url__ = "https://panel.sendcloud.sc/api/v3"
    __ref__ = "https://sendcloud.dev/api/v3"
    __timeout__ = 60

    def request(
        self, method, path, auth, accept="application/json", allow=(), **kwargs
    ):
        url = path if path.startswith("http") else f"{self.__url__}{path}"
        try:
            response = requests.request(
                method,
                url,
                auth=(auth.login, auth.password),
                headers={"Accept": accept},
                timeout=self.__timeout__,
                **kwargs,
            )
        except requests.RequestException as e:
            raise CarrierError(None, msg=[{"id": "Network", "message": str(e)}]) from e
        if response.status_code not in allow:
            self.raise_for_status(response)
        return response

    def raise_for_status(self, response):
        if response.ok:
            return
        try:
            errors = response.json().get("errors") or []
        except ValueError:
            errors = []
        raise CarrierError(
            response,
            msg=[
                {
                    "id": error.get("code") or response.status_code,
                    "message": " ".join(
                        part
                        for part in (
                            (error.get("source") or {}).get("pointer"),
                            error.get("detail"),
                        )
                        if part
                    ),
                }
                for error in errors
            ]
            or [{"id": response.status_code, "message": response.text}],
        )

    def get_document(self, auth, parcel, service):
        """Download the label of a parcel, for multi-parcel shipments where
        `label_file` is not returned."""
        link = next(
            (
                document["link"]
                for document in parcel.get("documents") or []
                if document.get("document_type", document.get("type")) == "label"
            ),
            f"{self.__url__}/parcels/{parcel['id']}/documents/label",
        )
        response = self.request(
            "GET",
            link,
            auth,
            accept=service.mime_type,
            params={"dpi": service.dpi} if service.dpi else None,
        )
        return b64encode(response.content).decode("utf-8")

    @action
    def get_label(self, input: SendcloudLabelInput) -> SendcloudLabelOutput:
        response = self.request(
            "POST", "/shipments/announce", input.auth, json=input.to_request()
        )
        parcels = response.json()["data"]["parcels"]
        for parcel in parcels:
            status = (parcel.get("status") or {}).get("code")
            if status == "ANNOUNCEMENT_FAILED":
                raise CarrierError(
                    response,
                    msg=[
                        {
                            "id": status,
                            "message": parcel["status"].get("message") or status,
                        }
                    ],
                )
        labels = [
            parcel.get("label_file")
            or self.get_document(input.auth, parcel, input.service)
            for parcel in parcels
        ]
        return SendcloudLabelOutput.from_response(input, parcels, labels)

    @action
    def search_pickup_sites(
        self, input: SendcloudPickupSiteSearchInput
    ) -> SendcloudPickupSiteSearchOutput:
        response = self.request(
            "GET", "/service-points", input.auth, params=input.search.to_params()
        )
        return SendcloudPickupSiteSearchOutput.from_response(response.json())

    @action
    def get_pickup_site(
        self, input: PickupSiteGetInput
    ) -> SendcloudPickupSiteGetOutput:
        response = self.request(
            "GET", f"/service-points/{input.get.id}", input.auth, allow=(404,)
        )
        if response.status_code == 404:
            return SendcloudPickupSiteGetOutput(site=None)
        return SendcloudPickupSiteGetOutput.from_response(response.json())
