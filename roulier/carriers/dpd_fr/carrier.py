# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import zeep

from ...schema import Metadata, MetaAddressFormat, MetaOption, MetaOptionType
from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import DpdFrLabelInput, DpdFrLabelOutput, Format, Notifications, Product


class DpdFr(Carrier):
    """
    DPD France carrier integration.
    This carrier allows you to create shipments and generate labels
    for DPD France services.

    The carrier supports the following features:
    - Create shipments with labels
    - Generate labels in different formats (PDF, PNG, ZPL, etc.)
    - Support for different products (DPD Classic, DPD Predict, etc.)
    - Support for notifications (Predict, Automatic SMS, etc.)

    The carrier requires the following parameters to be set:
    - `login`: The login ID for the DPD France web service.
    - `password`: The password for the DPD France web service.
    - `customerCountry`: The country code of the customer.
    - `customerId`: The customer ID for the DPD France web service.
    - `agencyId`: The agency ID for the DPD France web service.
    - `isTest`: A boolean value indicating whether to use the test environment.
    - `product`: The product to be used for the shipment (DPD Classic, DPD Predict, etc.)
    - `notifications`: The notifications to be used for the shipment (Predict, Automatic SMS, etc.)
    - `labelFormat`: The format of the label to be generated (PDF, PNG, ZPL, etc.)
    - `shippingDate`: The date of the shipment.
    """

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
        try:
            result = client.service.CreateShipmentWithLabelsBc(**input.soap(client))
        except zeep.exceptions.Fault as e:
            error_id = e.detail.xpath("//ErrorId")
            if len(error_id) > 0:
                error_id = error_id[0].text
            else:
                error_id = "UnknownError"
            raise CarrierError(None, msg=[{"id": error_id, "message": str(e)}]) from e
        return DpdFrLabelOutput.from_soap(result, input.service.labelFormat)

    @action
    def get_metadata(self) -> Metadata:
        return Metadata(
            documentation=self.__doc__,
            address_format=MetaAddressFormat(
                count=2,
                max_length=70,
            ),
            options=[
                MetaOption(
                    name="labelFormat",
                    label="Label Format",
                    description="Format of the label to be generated",
                    type=MetaOptionType.select,
                    default="PDF",
                    values=Format.__members__.values(),
                ),
                MetaOption(
                    name="product",
                    label="Product",
                    description="Product to be used for the shipment",
                    type=MetaOptionType.select,
                    default=Product.DPD_Classic,
                    values=Product.__members__.values(),
                ),
                MetaOption(
                    name="notifications",
                    label="Notifications",
                    description="Notifications to be used for the shipment",
                    type=MetaOptionType.select,
                    default=Notifications.No,
                    values=Notifications.__members__.values(),
                ),
                MetaOption(
                    name="agencyId",
                    label="Agency ID",
                    description="ID of the agency to be used for the shipment",
                ),
                MetaOption(
                    name="customerId",
                    label="Customer ID",
                    description="ID of the customer to be used for the shipment",
                ),
                MetaOption(
                    name="customerCountry",
                    label="Customer Country",
                    description="Country of the customer to be used for the shipment",
                    default="FR",
                ),
                MetaOption(
                    name="isTest",
                    label="Test Mode",
                    description="Use test mode for the shipment",
                    type=MetaOptionType.boolean,
                    default=False,
                ),
            ],
        )
