# -*- coding: utf-8 -*-
"""Transform input to ups compatible json."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from datetime import datetime
from .ups_api import UpsApi
from roulier.exception import InvalidApiInput
import logging

log = logging.getLogger(__name__)


class UpsEncoder(Encoder):
    """Transform input to ups compatible json."""

    def encode(self, api_input, action):
        """Transform input to Ups compatible json."""

        api = UpsApi()
        if not api.validate(api_input):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input))
        data = api.normalize(api_input)
        from_address = data["from_address"]
        to_address = data["to_address"]
        payload = dict(
            ShipmentRequest=dict(
                LabelSpecification=dict(
                    LabelImageFormat=dict(
                        Code=data.get("service").get("labelFormat", "GIF"),
                    ),
                    LabelStockSize=dict(
                        Height="6",
                        Width="4",
                    ),
                ),
                Shipment=dict(
                    Description=data.get('service').get('reference1', ""),
                    Shipper=dict(
                        Name=from_address.get('company') or from_address.get("name"),
                        AttentionName=from_address.get("name"),
                        TaxIdentificationNumber=from_address.get("vat"),
                        Phone=dict(Number=from_address.get("phone")),
                        EMailAddress=from_address.get("email"),
                        Address=dict(
                            AddressLine=[from_address.get("street1"), from_address.get("street2")],
                            City=from_address.get("city"),
            #                StateProvinceCode=from_address.get("state_code"),
                            PostalCode=from_address.get("zip"),
                            CountryCode=from_address.get("country"),
                        ),
                        ShipperNumber=data.get("auth").get("shipper_number"),
                    ),
                    ShipTo=dict(
                        Name=to_address.get('company') or to_address.get("name"),
                        AttentionName=to_address.get("name"),
                        TaxIdentificationNumber=to_address.get("vat"),
                        Phone=dict(Number=to_address.get("phone")),
                        EMailAddress=to_address.get("email"),
                        Address=dict(
                            AddressLine=[to_address.get("street1"), to_address.get("street2")],
                            City=to_address.get("city"),
            #                StateProvinceCode=to_address.get("state_code"),
                            PostalCode=to_address.get("zip"),
                            CountryCode=to_address.get("country"),
                        ),
                    ),
                    ShipFrom=dict(
                        Name=from_address.get('company') or from_address.get("name"),
                        AttentionName=from_address.get("name"),
                        TaxIdentificationNumber=from_address.get("vat"),
                        Phone=dict(Number=from_address.get("phone")),
                        EMailAddress=from_address.get("email"),
                        Address=dict(
                            AddressLine=[from_address.get("street1"), from_address.get("street2")],
                            City=from_address.get("city"),
            #                StateProvinceCode=from_address.get("state_code"),
                            PostalCode=from_address.get("zip"),
                            CountryCode=from_address.get("country"),
                        ),
                    ),
                    PaymentInformation=dict(
                        ShipmentCharge=dict(
                            Type="01",
                            BillShipper=dict(
                                # we ignore the alternatives paying per credit card or
                                # paypal for now
                                AccountNumber=data.get("auth").get("shipper_number"),
                            ),
                        ),
                    ),
                    Service=dict(
                        Code=data.get("service").get("product"),
                    ),
                    Package=[
                        dict(
                            ReferenceNumber=dict(
                                Value=package.get("reference"),
                            ),
                            Description=package.get("reference"),
                            NumOfPieces=str(package.get("number_of_pieces", "")),
                            Packaging=dict(
                                # fall back to 'Customer supplied package' if unset
                                Code=package.get("packaging_code"),
                            ),
#                            Dimensions=dict(
#                                UnitOfMeasurement=dict(Code="CM"),
#                                Length=str(package.packaging_id.length),
#                                Width=str(package.packaging_id.width),
#                                Height=str(package.packaging_id.height),
#                            ),
                            PackageWeight=dict(
                                UnitOfMeasurement=dict(Code=package.get("weight_unit")),
                                Weight=str(package.get("weight")),
                            ),
                        )
                        for package in data.get("parcels")
                    ],
                ),
            )
        )
        header = {
            "AccessLicenseNumber": data.get("auth").get("license_number"),
            "Username": data.get("auth").get("login"),
            "Password": data.get("auth").get("password"),
            "transactionSrc": data.get("auth").get("transaction_source"),
            "is_test": data.get("auth").get("isTest"),
        }
        return payload, header

    def api(self):
        """Return API we are expecting."""
        return UpsApi().api_values()
