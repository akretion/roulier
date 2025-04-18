# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64encode
from datetime import date
from enum import Enum
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from zeep import xsd

from ...schema import (
    LabelInput,
    Address,
    LabelOutput,
    Auth,
    Service,
    Parcel,
    ParcelLabel,
    Label,
    Tracking,
)


class Format(str, Enum):
    PNG = "PNG"
    PDF = "PDF"
    PDF_A6 = "PDF_A6"
    ZPL = "ZPL"
    ZPL300 = "ZPL300"
    ZPL_A6 = "ZPL_A6"
    ZPL300_A6 = "ZPL300_A6"
    EPL = "EPL"


class Notifications(str, Enum):
    No = "No"
    Predict = "Predict"
    AutomaticSMS = "AutomaticSMS"
    AutomaticMail = "AutomaticMail"


class Product(str, Enum):
    DPD_Classic = "DPD_Classic"
    DPD_Predict = "DPD_Predict"
    DPD_Relais = "DPD_Relais"


class DpdFrAuth(Auth):
    login: str

    def soap(self):
        return xsd.Element(
            "UserCredentials",
            xsd.ComplexType(
                [
                    xsd.Element("userid", xsd.String()),
                    xsd.Element("password", xsd.String()),
                ]
            ),
        )(
            userid=self.login,
            password=self.password,
        )


def dpd_service_validator(service):
    if (
        service.product in (Product.DPD_Predict, Product.DPD_Classic)
        and service.pickupLocationId
    ):
        raise ValueError(f"pickupLocationId can't be used with {service.product}")

    if service.product == Product.DPD_Predict:
        if service.notifications != Notifications.Predict:
            raise ValueError("Predict notifications must be set to Predict")
    else:
        if service.notifications == Notifications.Predict:
            raise ValueError(
                f"Predict notifications can't be used with {service.product}"
            )
        if service.product == Product.DPD_Relais and not service.pickupLocationId:
            raise ValueError("pickupLocationId is mandatory for Relais")

    return service


class DpdFrService(Service):
    labelFormat: Format = Format.PDF
    agencyId: str
    customerCountry: str
    customerId: str
    shippingDate: date | None = None
    notifications: Notifications = Notifications.No
    product: Product = Product.DPD_Classic
    pickupLocationId: str | None = None

    def soap(self, client, phone, email, ref):
        service = client.get_type("ns0:StdServices")
        contact = client.get_type("ns0:Contact")
        label_type = client.get_type("ns0:LabelType")
        ref_in_barcode = client.get_type("ns0:ReferenceInBarcode")

        service_kwargs = {
            "contact": contact(sms=phone, email=email, type=self.notifications.value),
        }

        if self.product == Product.DPD_Relais:
            parcel_shop = client.get_type("ns0:ParcelShop")
            shop_address = client.get_type("ns0:ShopAddress")
            service_kwargs.update(
                {
                    "parcelshop": parcel_shop(
                        shopaddress=shop_address(
                            shopid=self.pickupLocationId,
                        )
                    )
                }
            )

        return {
            "customer_countrycode": self.customerCountry,
            "customer_centernumber": self.agencyId,
            "customer_number": self.customerId,
            "referencenumber": self.reference1,
            "reference2": self.reference2 or ref,
            "reference3": self.reference3,
            "refnrasbarcode": str(bool(self.reference2)).lower(),
            "referenceInBarcode": ref_in_barcode(type="Reference2"),
            "shippingdate": self.shippingDate.strftime("%d/%m/%Y"),
            "labelType": label_type(
                type=(
                    self.labelFormat.value
                    if self.labelFormat != Format.PNG
                    else "Default"
                )
            ),
            "services": service(
                **service_kwargs,
            ),
        }


class DpdFrParcel(Parcel):
    def soap(self):
        return {
            "weight": self.weight,
        }


class DpdFrAddress(Address):
    country: str
    zip: str
    city: str
    street1: str
    name2: str | None = None
    name3: str | None = None
    name4: str | None = None
    door1: str | None = None
    door2: str | None = None
    intercom: str | None = None

    def soap(self, client):
        address = client.get_type("ns0:Address")
        address_info = client.get_type("ns0:AddressInfo")
        return {
            "address": address(
                name=", ".join(
                    [part for part in (self.name, self.company) if part],
                )[0:35],
                countryPrefix=self.country,
                zipCode=self.zip,
                city=self.city,
                street=", ".join(
                    [part for part in (self.street1, self.street2) if part]
                )[0:70],
                phoneNumber=self.phone,
            ),
            "info": address_info(
                contact=self.company,
                name2=self.name2,
                name3=self.name3,
                name4=self.name4,
                digicode1=self.door1,
                digicode2=self.door2,
                intercomid=self.intercom,
                vinfo1=(
                    self.delivery_instructions[0:35]
                    if getattr(self, "delivery_instructions", None)
                    else None
                ),
                vinfo2=(
                    self.delivery_instructions[35:70]
                    if getattr(self, "delivery_instructions", None)
                    and len(self.delivery_instructions) > 35
                    else None
                ),
            ),
        }


class DpdFrFromAddress(DpdFrAddress):
    phone: str

    def soap(self, client):
        rv = super().soap(client)
        return {
            "shipperaddress": rv["address"],
            "shipperinfo": rv["info"],
        }


class DpdFrToAddress(DpdFrAddress):
    def soap(self, client):
        rv = super().soap(client)
        return {
            "receiveraddress": rv["address"],
            "receiverinfo": rv["info"],
        }


class DpdFrLabelInput(LabelInput):
    auth: DpdFrAuth
    service: Annotated[DpdFrService, AfterValidator(dpd_service_validator)]
    parcels: list[DpdFrParcel]
    from_address: DpdFrFromAddress
    to_address: DpdFrToAddress

    def soap(self, client):
        request = client.get_type("ns0:StdShipmentLabelRequest")
        request_kwargs = {
            **self.service.soap(
                client,
                self.to_address.phone,
                self.to_address.email,
                self.parcels[0].reference,
            ),
            **self.parcels[0].soap(),
            **self.from_address.soap(client),
            **self.to_address.soap(client),
        }

        return {
            "_soapheaders": [self.auth.soap()],
            "request": request(**request_kwargs),
        }


class DpdFrLabel(Label):
    @classmethod
    def from_soap(cls, result, format):
        return cls.model_construct(
            data=b64encode(result["label"]).decode("utf-8"),
            name=f"{format.value} Label",
            type=format.value,
        )


class DpdFrTracking(Tracking):
    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(
            number=result["BarcodeId"],
        )


class DpdFrParcelLabel(ParcelLabel):
    label: DpdFrLabel | None = None
    barcode: str | None = None

    @classmethod
    def from_soap(cls, id, shipment, label, input):
        return cls.model_construct(
            id=id,
            label=DpdFrLabel.from_soap(label, input.service.labelFormat),
            reference=input.parcels[0].reference,
            barcode=shipment["Shipment"]["BarCode"],
            tracking=DpdFrTracking.from_soap(shipment["Shipment"]),
        )


class DpdFrLabelOutput(LabelOutput):
    parcels: list[DpdFrParcelLabel]

    @classmethod
    def from_soap(cls, result, input):
        shipments = result["shipments"]["ShipmentBc"]
        labels = result["labels"]["Label"]
        assert len(shipments) == len(labels), "Mismatched shipments and labels"
        parcels = zip(shipments, labels)
        return cls.model_construct(
            parcels=[
                DpdFrParcelLabel.from_soap(i + 1, shipment, label, input)
                for i, (shipment, label) in enumerate(parcels)
            ]
        )
