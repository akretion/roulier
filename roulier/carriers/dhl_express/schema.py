# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64encode
from datetime import date, datetime, timezone
from enum import Enum

from pydantic import BaseModel

from ...helpers import filter_empty, merge, unaccent
from ...schema import (
    Address,
    Auth,
    Label,
    LabelInput,
    LabelOutput,
    Parcel,
    ParcelLabel,
    Service,
    Tracking,
)


class Format(Enum):
    PDF = "PDF"
    ZPL = "ZPL"
    DPL = "LP2"
    EPL = "EPL"


class DocumentFormat(Enum):
    PDF = "PDF"
    PNG = "PNG"
    GIF = "GIF"
    TIFF = "TIFF"
    JPEG = "JPEG"


class Incoterm(Enum):
    EXW = "EXW"
    FCA = "FCA"
    CPT = "CPT"
    CIP = "CIP"
    DPU = "DPU"
    DAP = "DAP"
    DDP = "DDP"
    FAS = "FAS"
    FOB = "FOB"
    CFR = "CFR"
    CIF = "CIF"
    DAF = "DAF"
    DAT = "DAT"
    DDU = "DDU"
    DEQ = "DEQ"
    DES = "DES"


class AccountType(Enum):
    SHIPPER = "shipper"
    PAYER = "payer"
    DUTIES_AND_TAXES = "duties-taxes"


class ReferenceType(Enum):
    AAO = "AAO"
    CU = "CU"
    FF = "FF"
    FN = "FN"
    IBC = "IBC"
    LLR = "LLR"
    OBC = "OBC"
    PRN = "PRN"
    ACP = "ACP"
    ACS = "ACS"
    ACR = "ACR"
    CDN = "CDN"
    STD = "STD"
    CO = "CO"
    AFM = "AFM"


class UoM(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class ProductUoM(Enum):
    BOX = "BOX"
    _2GM = "2GM"
    M3 = "M3"
    DPR = "DPR"
    DOZ = "DOZ"
    PCS = "PCS"
    GM = "GM"
    GRS = "GRS"
    KG = "KG"
    M = "M"
    _3GM = "3GM"
    X = "X"
    NO = "NO"
    PRS = "PRS"
    CM2 = "CM2"
    _2M2 = "2M2"
    _3M2 = "3M2"
    M2 = "M2"
    _4M2 = "4M2"
    CM = "CM"
    CONE = "CONE"
    CT = "CT"
    EA = "EA"
    LBS = "LBS"
    RILL = "RILL"
    ROLL = "ROLL"
    SET = "SET"
    TU = "TU"
    KM = "KM"
    IN = "IN"
    FT = "FT"
    YD = "YD"
    MI = "MI"
    LTR = "LTR"
    MMQ = "MMQ"
    CM3 = "CM3"
    DMQ = "DMQ"
    MLT = "MLT"
    CLT = "CLT"
    DLT = "DLT"
    INQ = "INQ"
    FT3 = "FT3"
    YD3 = "YD3"
    GLI = "GLI"
    GLL = "GLL"
    PT = "PT"
    PTI = "PTI"
    QTI = "QTI"
    PTL = "PTL"
    QTL = "QTL"
    PTD = "PTD"
    OZI = "OZI"
    J57 = "J57"
    NM3 = "NM3"
    SM3 = "SM3"
    TNE = "TNE"
    LB = "LB"
    ONZ = "ONZ"
    CEL = "CEL"


class ExportType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    RETURN = "return"
    USED_EXHIBITION_GOODS_TO_ORIGIN = "used_exhibition_goods_to_origin"
    INTERCOMPANY_USE = "intercompany_use"
    COMMERCIAL_PURPOSE_OR_SALE = "commercial_purpose_or_sale"
    PERSONAL_BELONGINGS_OR_PERSONAL_USE = "personal_belongings_or_personal_use"
    SAMPLE = "sample"
    GIFT = "gift"
    RETURN_TO_ORIGIN = "return_to_origin"
    WARRANTY_REPLACEMENT = "warranty_replacement"
    DIPLOMATIC_GOODS = "diplomatic_goods"
    DEFENCE_MATERIAL = "defence_material"


class DHLExpressAuth(Auth):
    login: str
    password: str

    def params(self):
        return {
            "authorization": "Basic "
            + b64encode(f"{self.login}:{self.password}".encode()).decode()
        }


class DHLExpressAddress(Address):
    country: str
    zip: str
    city: str
    street1: str
    street2: str | None = None
    street3: str | None = None
    phone: str
    landlinePhone: str | None = None
    stateOrProvinceCode: str | None = None

    def params(self):
        return {
            "postalAddress": {
                "postalCode": self.zip,
                "cityName": self.city,
                "countryCode": self.country,
                "provinceCode": self.stateOrProvinceCode,
                "addressLine1": self.street1,
                "addressLine2": self.street2,
                "addressLine3": self.street3,
            },
            "contactInformation": {
                "phone": self.landlinePhone or self.phone,
                "mobilePhone": self.phone,
                "companyName": self.company or self.name,
                "fullName": self.name,
                "email": self.email,
            },
        }


class DHLExpressService(Service):
    shippingDate: datetime
    labelFormat: Format | None = Format.PDF
    shipmentDescription: str | None = None
    incoterm: Incoterm = Incoterm.DAP
    unitOfMeasurement: UoM | None = UoM.METRIC
    accountType: AccountType | None = AccountType.SHIPPER
    referenceType: ReferenceType | None = ReferenceType.CU
    product: str
    pickupLocationId: str | None = None

    def params(self):
        shipping_date = self.shippingDate
        if shipping_date.tzinfo is None:
            shipping_date = shipping_date.replace(tzinfo=timezone.utc)

        shipping_date = shipping_date.isoformat(timespec="seconds")
        shipping_date = shipping_date.replace("+", " GMT+")
        return {
            "productCode": self.product,
            "plannedShippingDateAndTime": shipping_date,
            "pickup": {
                "isRequested": self.pickupLocationId is not None,
                "location": self.pickupLocationId,
            },
            "content": {
                "description": self.shipmentDescription or "N/A",
                "incoterm": self.incoterm.value,
                "unitOfMeasurement": self.unitOfMeasurement.value
                if self.unitOfMeasurement
                else UoM.METRIC.value,
            },
            "outputImageProperties": {
                "encodingFormat": (
                    self.labelFormat.value if self.labelFormat else Format.PDF.value
                ).lower(),
                "imageOptions": [
                    {
                        "typeCode": "label",
                        "templateName": "ECOM26_64_002",
                    }
                ],
                "allDocumentsInOneImage": False,
                "splitTransportAndWaybillDocLabels": True,
                "receiptAndLabelsInOneImage": False,
            },
            "accounts": [
                {
                    "number": self.customerId,
                    "typeCode": self.accountType.value
                    if self.accountType
                    else AccountType.SHIPPER.value,
                }
            ],
            "customerReferences": [
                {
                    "value": self.reference1,
                    "typeCode": self.referenceType.value
                    if self.referenceType
                    else ReferenceType.CU.value,
                }
            ],
        }


class DHLExpressArticle(BaseModel):
    number: int | None = None
    description: str
    value: float
    quantity: int
    uom: ProductUoM | None = ProductUoM.PCS
    weight: float | None = None
    weightGross: float | None = None
    originCountry: str
    exportType: ExportType | None = ExportType.COMMERCIAL_PURPOSE_OR_SALE

    hsCode: str
    inboundHsCode: str | None = None

    def params(self, i):
        return {
            "number": self.number or i + 1,
            "description": self.description,
            "price": self.value,
            "quantity": {
                "value": self.quantity,
                "unitOfMeasurement": self.uom.value
                if self.uom
                else ProductUoM.PCS.value,
            },
            "commodityCodes": [
                {"typeCode": "outbound", "value": self.hsCode},
                {"typeCode": "inbound", "value": self.inboundHsCode or self.hsCode},
            ],
            "exportReasonType": self.exportType.value
            if self.exportType
            else ExportType.COMMERCIAL_PURPOSE_OR_SALE.value,
            "manufacturerCountry": self.originCountry,
            "weight": {
                "netValue": self.weight if self.weight else None,
                "grossValue": self.weightGross if self.weightGross else None,
            },
        }


class DHLExpressInvoice(BaseModel):
    number: str
    content: str
    date: date
    format: DocumentFormat | None = DocumentFormat.PDF

    def params(self):
        return {
            "content": {
                "exportDeclaration": {
                    "invoice": {
                        "number": self.number,
                        "date": self.date.strftime("%Y-%m-%d"),
                    },
                }
            },
            "documentImages": [
                {
                    "imageFormat": DocumentFormat.PDF.value
                    if self.format
                    else DocumentFormat.PDF.value,
                    "content": self.content,
                    "typeCode": "INV",
                }
            ],
        }


class DHLExpressCustoms(BaseModel):
    invoice: DHLExpressInvoice
    numberOfCopies: int | None = None
    articles: list[DHLExpressArticle] = []
    vat: float | None = None
    delivery: float | None = None
    insurance: float | None = None

    def params(self):
        return merge(
            self.invoice.params(),
            {
                "content": {
                    "isCustomsDeclarable": True,
                    "exportDeclaration": {
                        "lineItems": [
                            article.params(i) for i, article in enumerate(self.articles)
                        ],
                        "additionalCharges": (
                            [
                                {
                                    "caption": "Freight",
                                    "value": self.delivery,
                                    "typeCode": "freight",
                                }
                            ]
                            if self.delivery
                            else []
                        )
                        + (
                            [
                                {
                                    "caption": "Insurance",
                                    "value": self.insurance,
                                    "typeCode": "insurance",
                                }
                            ]
                            if self.insurance
                            else []
                        )
                        + (
                            [
                                {
                                    "caption": "VAT",
                                    "value": self.vat,
                                    "typeCode": "vat",
                                }
                            ]
                            if self.vat
                            else []
                        ),
                    },
                    "declaredValueCurrency": "EUR",
                    "declaredValue": 1155.0,
                },
            },
            {
                "outputImageProperties": {
                    "imageOptions": [
                        {
                            "templateName": "COMMERCIAL_INVOICE_P_10",
                            "invoiceType": "commercial",
                            "isRequested": False,
                            "typeCode": "invoice",
                        }
                    ]
                }
            },
        )


class DHLExpressParcel(Parcel):
    length: float
    width: float
    height: float
    referenceType: ReferenceType | None = ReferenceType.CU

    def params(self):
        return {
            "weight": self.weight,
            # "typeCode":"2BP",
            "dimensions": {
                "length": self.length,
                "width": self.width,
                "height": self.height,
            },
            "customerReferences": [
                {
                    "value": self.reference,
                    "typeCode": self.referenceType.value
                    if self.referenceType
                    else ReferenceType.CU.value,
                }
            ],
        }


class DHLExpressLabelInput(LabelInput):
    auth: DHLExpressAuth
    service: DHLExpressService
    parcels: list[DHLExpressParcel]
    to_address: DHLExpressAddress
    from_address: DHLExpressAddress
    customs: DHLExpressCustoms | None = None

    def params(self):
        return unaccent(
            filter_empty(
                merge(
                    self.auth.params(),
                    self.service.params(),
                    {
                        "content": {
                            "packages": [parcel.params() for parcel in self.parcels],
                        }
                    },
                    {
                        "customerDetails": {
                            "shipperDetails": self.from_address.params(),
                            "receiverDetails": self.to_address.params(),
                        }
                    },
                    self.customs.params()
                    if self.customs
                    else {
                        "content": {
                            "isCustomsDeclarable": False,
                        }
                    },
                )
            )
        )


class DHLExpressTracking(Tracking):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            number=result["trackingNumber"],
            url=result.get("trackingUrl"),
        )


class DHLExpressLabel(Label):
    @classmethod
    def from_params(cls, result, name, format):
        return cls.model_construct(
            data=result,
            name=name,
            type=format,
        )


class DHLExpressParcelLabel(ParcelLabel):
    label: DHLExpressLabel | None = None
    tracking: DHLExpressTracking | None = None

    @classmethod
    def from_params(cls, result, document, input, id):
        return cls.model_construct(
            id=id,
            reference=input.parcels[result["referenceNumber"] - 1].reference,
            label=(
                DHLExpressLabel.from_params(
                    document["content"], "label", document["imageFormat"]
                )
            ),
            tracking=DHLExpressTracking.from_params(result),
        )


class DHLExpressLabelOutput(LabelOutput):
    shipmentTrackingNumber: str
    shipmentTrackingUrl: str | None = None
    parcels: list[DHLExpressParcelLabel]
    annexes: list[DHLExpressLabel]

    @classmethod
    def from_params(cls, results, input):
        labels_by_referrence = {
            document.get("packageReferenceNumber"): document
            for document in results.get("documents", [])
            if document["typeCode"] == "label"
        }
        return cls.model_construct(
            shipmentTrackingNumber=results["shipmentTrackingNumber"],
            shipmentTrackingUrl=results.get("trackingUrl"),
            parcels=[
                DHLExpressParcelLabel.from_params(
                    result,
                    labels_by_referrence.get(
                        result["referenceNumber"], labels_by_referrence.get(None)
                    ),
                    input,
                    i + 1,
                )
                for i, result in enumerate(results["packages"])
            ],
            annexes=[
                DHLExpressLabel.from_params(
                    document["content"], document["typeCode"], document["imageFormat"]
                )
                for document in results.get("documents", [])
                if document["typeCode"] != "label"
            ],
        )
