# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import zeep

from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import DpdFrLabelInput, DpdFrLabelOutput
from ...helpers import expand_multi_parcels, factorize_multi_parcels


class DpdFr(Carrier):
    __key__ = "dpd_fr"
    __url__ = (
        "https://e-station.cargonet.software/dpd-eprintwebservice/eprintwebservice.asmx"
    )
    __url_test__ = "https://e-station-testenv.cargonet.software/eprintwebservice/eprintwebservice.asmx"
    __ns_prefix__ = "http://www.cargonet.software"

    def _get_client(self, is_test):
        url = self.__url_test__ if is_test else self.__url__
        client = zeep.Client(wsdl=f"{url}?WSDL")
        client.set_ns_prefix(None, self.__ns_prefix__)
        return client

    @action
    def get_label(self, input: DpdFrLabelInput) -> DpdFrLabelOutput:
        client = self._get_client(input.auth.isTest)
        results = []
        for input_mono_parcel in expand_multi_parcels(input):
            try:
                results.append(
                    DpdFrLabelOutput.from_soap(
                        client.service.CreateShipmentWithLabelsBc(
                            **input_mono_parcel.soap(client)
                        ),
                        input_mono_parcel,
                    )
                )

            except zeep.exceptions.Fault as e:
                error_id = e.detail.xpath("//ErrorId")
                if len(error_id) > 0:
                    error_id = error_id[0].text
                else:
                    error_id = "UnknownError"
                raise CarrierError(
                    None, msg=[{"id": error_id, "message": str(e)}]
                ) from e

        return factorize_multi_parcels(results)
