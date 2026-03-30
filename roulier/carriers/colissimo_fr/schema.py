# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64encode
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, model_validator

from ...helpers import merge, unaccent
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
    PickupSite,
    PickupSiteSearchInput,
    PickupSiteSearch,
    PickupSiteGetInput,
    PickupSiteGet,
    PickupSiteOpeningSlot,
    PickupSiteOpeningHours,
    PickupSiteSearchOutput,
    PickupSiteGetOutput,
    PackingSlipInput,
    PackingSlipOutput,
    PackingSlip,
    PackingSlipClient,
    PackingSlipSupportSite,
    DocumentService,
    GetDocumentService,
    GetDocumentInput,
    GetDocumentsInput,
    CreateUpdateDocumentService,
    CreateUpdateDocumentInput,
    DocumentOutput,
)


class Format(Enum):
    # Shortcuts
    PDF = "PDF"
    ZPL = "ZPL"
    DPL = "DPL"
    # Formats
    ZPL_10x15_203dpi = "ZPL_10x15_203dpi"
    ZPL_10x15_300dpi = "ZPL_10x15_300dpi"
    DPL_10x15_203dpi = "DPL_10x15_203dpi"
    DPL_10x15_300dpi = "DPL_10x15_300dpi"
    PDF_10x15_300dpi = "PDF_10x15_300dpi"
    PDF_A4_300dpi = "PDF_A4_300dpi"
    ZPL_10x10_203dpi = "ZPL_10x10_203dpi"
    ZPL_10x10_300dpi = "ZPL_10x10_300dpi"
    DPL_10x10_203dpi = "DPL_10x10_203dpi"
    DPL_10x10_300dpi = "DPL_10x10_300dpi"
    PDF_10x10_300dpi = "PDF_10x10_300dpi"
    ZPL_10x15_203dpi_UL = "ZPL_10x15_203dpi_UL"
    ZPL_10x15_300dpi_UL = "ZPL_10x15_300dpi_UL"
    DPL_10x15_203dpi_UL = "DPL_10x15_203dpi_UL"
    DPL_10x15_300dpi_UL = "DPL_10x15_300dpi_UL"
    PDF_10x15_300dpi_UL = "PDF_10x15_300dpi_UL"
    PDF_A4_300dpi_UL = "PDF_A4_300dpi_UL"

    @property
    def final_value(self):
        return (
            {
                Format.PDF: Format.PDF_10x15_300dpi,
                Format.ZPL: Format.ZPL_10x15_300dpi,
                Format.DPL: Format.DPL_10x15_300dpi,
            }
            .get(self, self)
            .value
        )


class ColissimoFrAuth(Auth):
    login: str | None = None
    password: str | None = None
    apiKey: str | None = None

    def params(self):
        if self.apiKey:
            return {"apiKey": self.apiKey}
        return {
            "contractNumber": self.login,
            "password": self.password,
        }

    @model_validator(mode="after")
    def check_login_pass_or_apikey(self):
        if self.apiKey:
            if self.login or self.password:
                raise ValueError("Only one of login/password or apiKey is allowed")
        else:
            if not self.login or not self.password:
                raise ValueError("Without apiKey, login and password are required")

        return self


class ColissimoFrAddress(Address):
    country: str
    firstName: str | None = None
    zip: str
    city: str
    street0: str | None = None
    street1: str
    street2: str | None = None
    street3: str | None = None
    door1: str | None = None
    door2: str | None = None
    intercom: str | None = None
    language: str = "FR"
    landlinePhone: str | None = None
    stateOrProvinceCode: str | None = None

    def params(self):
        return {
            "companyName": self.company,
            "lastName": self.name,
            "firstName": self.firstName,
            "line0": self.street2,
            "line1": self.street0,
            "line2": self.street1,
            "line3": self.street3,
            "countryCode": self.country,
            "city": self.city,
            "zipCode": self.zip,
            "phoneNumber": self.landlinePhone,
            "mobileNumber": self.phone,
            "doorCode1": self.door1,
            "doorCode2": self.door2,
            "intercom": self.intercom,
            "email": self.email,
            "language": self.language,
            "stateOrProvinceCode": self.stateOrProvinceCode,
        }


class ColissimoFrService(Service):
    labelFormat_x: int = 0
    labelFormat_y: int = 0
    labelFormat: Format | None = Format.PDF
    dematerialized: bool = False
    returnType: str | None = None
    printCoDDocument: bool = False

    product: str
    pickupLocationId: str | None = None

    mailBoxPicking: bool = False
    mailBoxPickingDate: date | None = None
    vatCode: int | None = None
    vatPercentage: int | None = None
    vatAmount: int | None = None
    transportationAmount: int | None = None
    totalAmount: int | None = None
    commercialName: str | None = None
    returnTypeChoice: int | None = None
    reseauPostal: str | None = None

    codeBarForReference: bool | None = None
    serviceInfo: str | None = None
    promotionCode: str | None = None

    codSenderAddress: ColissimoFrAddress | None = None

    @model_validator(mode="after")
    def check_format(self):
        if self.labelFormat is None:
            self.labelFormat = Format.PDF
        return self

    def params(self):
        return {
            "outputFormat": {
                "x": self.labelFormat_x,
                "y": self.labelFormat_y,
                "outputPrintingType": self.labelFormat.final_value,
                "dematerialized": self.dematerialized,
                "returnType": self.returnType,
                "printCoDDocument": self.printCoDDocument,
            },
            "letter": {
                "service": {
                    "productCode": self.product,
                    "depositDate": self.shippingDate.isoformat(),
                    "mailBoxPicking": self.mailBoxPicking,
                    "mailBoxPickingDate": (
                        self.mailBoxPickingDate.isoformat()
                        if self.mailBoxPickingDate
                        else None
                    ),
                    "vatCode": self.vatCode,
                    "vatPercentage": self.vatPercentage,
                    "vatAmount": self.vatAmount,
                    "transportationAmount": self.transportationAmount,
                    "totalAmount": self.totalAmount,
                    "orderNumber": self.reference1,
                    "commercialName": self.commercialName,
                    "returnTypeChoice": self.returnTypeChoice,
                    "reseauPostal": self.reseauPostal,
                },
                "parcel": {
                    "pickupLocationId": self.pickupLocationId,
                },
                "sender": {
                    "senderParcelRef": self.reference1,
                },
                "addressee": {
                    "addresseeParcelRef": self.reference2,
                    "codeBarForReference": self.codeBarForReference,
                    "serviceInfo": self.serviceInfo,
                    "promotionCode": self.promotionCode,
                },
                "codSenderAddress": (
                    self.codSenderAddress.params() if self.codSenderAddress else None
                ),
            },
        }


class ColissimoFrArticle(BaseModel):
    description: str | None = None
    quantity: int | None = None
    weight: float | None = None
    value: float | None = None
    hsCode: str | None = None
    originCountry: str | None = None
    originCountryLabel: str | None = None
    currency: str | None = "EUR"
    artref: str | None = None
    originalIdent: str | None = None
    vatAmount: float | None = None
    customsFees: float | None = None

    def params(self):
        return {
            "description": self.description,
            "quantity": self.quantity,
            "weight": self.weight,
            "value": self.value,
            "hsCode": self.hsCode,
            "originCountry": self.originCountry,
            "originCountryLabel": self.originCountryLabel,
            "currency": self.currency,
            "artref": self.artref,
            "originalIdent": self.originalIdent,
            "vatAmount": self.vatAmount,
            "customsFees": self.customsFees,
        }


class ColissimoFrOriginal(BaseModel):
    originalIdent: str | None = None
    originalInvoiceNumber: str | None = None
    originalInvoiceDate: str | None = None
    originalParcelNumber: str | None = None

    def params(self):
        return {
            "originalIdent": self.originalIdent,
            "originalInvoiceNumber": self.originalInvoiceNumber,
            "originalInvoiceDate": self.originalInvoiceDate,
            "originalParcelNumber": self.originalParcelNumber,
        }


class ColissimoFrCustoms(BaseModel):
    includesCustomsDeclarations: bool = False
    numberOfCopies: int | None = None

    # contents
    articles: list[ColissimoFrArticle] = []
    category: int
    original: list[ColissimoFrOriginal] = []
    explanations: str | None = None

    importersReference: str | None = None
    importersContact: str | None = None
    officeOrigin: str | None = None
    comments: str | None = None
    description: str | None = None
    invoiceNumber: str | None = None
    licenseNumber: str | None = None
    certificatNumber: str | None = None
    importerAddress: ColissimoFrAddress | None = None

    def params(self):
        return {
            "includesCustomsDeclarations": True,
            "numberOfCopies": self.numberOfCopies,
            "contents": {
                "article": [article.params() for article in self.articles],
                "category": {
                    "value": self.category,
                },
                "original": [orig.params() for orig in self.original],
                "explanations": self.explanations,
            },
            "importersReference": self.importersReference,
            "importersContact": self.importersContact,
            "officeOrigin": self.officeOrigin,
            "comments": self.comments,
            "description": self.description,
            "invoiceNumber": self.invoiceNumber,
            "licenseNumber": self.licenseNumber,
            "certificatNumber": self.certificatNumber,
            "importerAddress": (
                self.importerAddress.params() if self.importerAddress else None
            ),
        }


class ColissimoFrParcel(Parcel):
    parcelNumber: str | None = None
    insuranceAmount: int | None = None
    insuranceValue: int | None = None
    recommendationLevel: str | None = None
    nonMachinable: bool = False
    returnReceipt: bool = False
    instructions: str | None = None
    pickupLocationId: str | None = None
    ftd: bool = False
    ddp: bool = False
    disabledDeliveryBlockingCode: str | None = None
    cod: bool = False
    codamount: int | None = None
    codcurrency: str | None = None

    customs: ColissimoFrCustoms | None = None

    length: int | None = None
    width: int | None = None
    height: int | None = None

    def params(self):
        return {
            "letter": {
                "parcel": {
                    "parcelNumber": self.parcelNumber,
                    "insuranceAmount": self.insuranceAmount,
                    "insuranceValue": self.insuranceValue,
                    "recommendationLevel": self.recommendationLevel,
                    "weight": self.weight,
                    "nonMachinable": self.nonMachinable,
                    "returnReceipt": self.returnReceipt,
                    "instructions": self.instructions,
                    "pickupLocationId": self.pickupLocationId,  # TODO
                    "ftd": self.ftd,
                    "ddp": self.ddp,
                    "disabledDeliveryBlockingCode": self.disabledDeliveryBlockingCode,
                    "cod": self.cod,
                    "codamount": self.codamount,
                    "codcurrency": self.codcurrency,
                },
                "customsDeclarations": self.customs.params() if self.customs else None,
            },
            "fields": (
                {
                    "field": [
                        {"key": key.upper(), "value": getattr(self, key)}
                        for key in ["length", "width", "height"]
                        if getattr(self, key)
                    ]
                }
                if self.length or self.width or self.height
                else None
            ),
        }


class ColissimoFrLabelInput(LabelInput):
    auth: ColissimoFrAuth
    service: ColissimoFrService
    parcels: list[ColissimoFrParcel]
    to_address: ColissimoFrAddress
    from_address: ColissimoFrAddress

    def params(self):
        return unaccent(
            merge(
                self.auth.params(),
                self.service.params(),
                self.parcels[0].params(),
                {
                    "letter": {
                        "sender": {"address": self.from_address.params()},
                        "addressee": {"address": self.to_address.params()},
                    }
                },
            )
        )


class ColissimoFrTracking(Tracking):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            number=result["parcelNumber"],
            url=result["pdfUrl"],
            partner=result["parcelNumberPartner"],
        )


class ColissimoFrLabel(Label):
    @classmethod
    def from_params(cls, result, name, format):
        return cls.model_construct(
            data=b64encode(result).decode("utf-8"),
            name=name,
            type=format,
        )


class ColissimoFrParcelLabel(ParcelLabel):
    label: ColissimoFrLabel | None = None
    tracking: ColissimoFrTracking | None = None

    @classmethod
    def from_params(cls, result, input):
        return cls.model_construct(
            id=1,
            reference=input.parcels[0].reference,
            label=(
                ColissimoFrLabel.from_params(
                    result["<label>"], "label", input.service.labelFormat.value
                )
                if "<label>" in result
                else None
            ),
            tracking=ColissimoFrTracking.from_params(
                result["<jsonInfos>"]["labelV2Response"]
            ),
        )


class ColissimoFrLabelOutput(LabelOutput):
    parcels: list[ColissimoFrParcelLabel]
    annexes: list[ColissimoFrLabel]

    @classmethod
    def from_params(cls, results, input):
        return cls.model_construct(
            parcels=[ColissimoFrParcelLabel.from_params(results, input)],
            annexes=[
                ColissimoFrLabel.from_params(
                    data, annex, input.service.labelFormat.value
                )
                for annex, data in results.items()
                if annex not in ["<label>", "<jsonInfos>"]
            ],
        )


class ColissimoFrPickingSiteAuth(ColissimoFrAuth):
    def params(self):
        rv = super().params()
        if "contractNumber" in rv:
            del rv["contractNumber"]

        return rv


class ColissimoFrPickupSiteService(Service):
    def params(self):
        return {
            "shippingDate": self.shippingDate.strftime("%d/%m/%Y")
            if self.shippingDate
            else None,
            "accountNumber": self.customerId,
        }


class ColissimoFrPickupSiteGetService(ColissimoFrPickupSiteService):
    def params(self):
        rv = super().params()
        rv["date"] = rv.pop("shippingDate")
        return rv


class ColissimoFrPickupSiteSearch(PickupSiteSearch):
    filter: str = "0"
    inter: str = "0"
    language: str = "FR"

    def params(self):
        return {
            "address": self.street,
            "zipCode": self.zip,
            "city": self.city,
            "countryCode": self.country,
            "weight": self.weight,
            "filterRelay": self.filter,
            "lang": self.language,
            "optionInter": self.inter,
        }


class ColissimoFrPickupSiteSearchInput(PickupSiteSearchInput):
    auth: ColissimoFrPickingSiteAuth
    search: ColissimoFrPickupSiteSearch
    service: ColissimoFrPickupSiteService

    def params(self):
        return unaccent(
            merge(
                self.auth.params(),
                self.search.params(),
                self.service.params(),
            )
        )


class ColissimoFrPickupSiteGet(PickupSiteGet):
    weight: float | None = None
    filter: str = "0"
    language: str = "FR"

    def params(self):
        return {
            "id": self.id,
            "weight": self.weight,
            "filterRelay": self.filter,
            "reseau": self.zone,
            "langue": self.language,
        }


class ColissimoFrPickupSiteGetInput(PickupSiteGetInput):
    auth: ColissimoFrPickingSiteAuth
    get: ColissimoFrPickupSiteGet
    service: ColissimoFrPickupSiteGetService

    def params(self):
        return unaccent(
            merge(
                self.auth.params(),
                self.get.params(),
                self.service.params(),
            )
        )


class ColissimoFrPickupSiteOpeningSlot(PickupSiteOpeningSlot):
    @classmethod
    def from_params(cls, start, end):
        return cls.model_construct(
            start=datetime.strptime(start, "%H:%M").time(),
            end=datetime.strptime(end, "%H:%M").time(),
        )


class ColissimoFrPickupSiteOpeningHours(PickupSiteOpeningHours):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            **{
                day: [
                    ColissimoFrPickupSiteOpeningSlot.from_params(slot_start, slot_end)
                    for slot in result[f"horairesOuverture{day_label}"].split(" ")
                    if slot
                    for slot_start, slot_end in [slot.split("-")]
                    if slot_start != "00:00" and slot_end != "00:00"
                ]
                for day, day_label in [
                    ("monday", "Lundi"),
                    ("tuesday", "Mardi"),
                    ("wednesday", "Mercredi"),
                    ("thursday", "Jeudi"),
                    ("friday", "Vendredi"),
                    ("saturday", "Samedi"),
                    ("sunday", "Dimanche"),
                ]
            }
        )


class ColissimoFrPickupSiteVacation(BaseModel):
    start: datetime
    end: datetime

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            start=datetime.fromtimestamp(
                result["calendarDeDebut"] / 1000, timezone.utc
            ),
            end=datetime.fromtimestamp(result["calendarDeFin"] / 1000, timezone.utc),
        )


class ColissimoFrPickupSite(PickupSite):
    details: str | None = None
    zone: str | None = None
    type: str | None = None
    max_weight: float | None = None
    distance: int | None = None
    parking: bool = False
    disabled_access: bool = False
    vacations: list[ColissimoFrPickupSiteVacation] = []

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            id=result["identifiant"],
            name=result["nom"],
            street="\n".join(
                [
                    part.strip()
                    for part in [
                        result["adresse1"],
                        result["adresse2"],
                        result["adresse3"],
                    ]
                    if part
                ]
            ),
            zip=result["codePostal"],
            city=result["localite"],
            details=result["indiceDeLocalisation"],
            country=result["codePays"],
            zone=result["reseau"],
            lat=result["coordGeolocalisationLatitude"],
            lng=result["coordGeolocalisationLongitude"],
            type=result["typeDePoint"],
            max_weight=result["poidsMaxi"],
            distance=result["distanceEnMetre"],
            hours=ColissimoFrPickupSiteOpeningHours.from_params(result),
            vacations=[
                ColissimoFrPickupSiteVacation.from_params(vacation)
                for vacation in result["listeConges"]
            ],
            parking=result["parking"],
            disabled_access=result["accesPersonneMobiliteReduite"],
        )


class ColissimoFrPickupSiteSearchOutput(PickupSiteSearchOutput):
    quality: int
    sites: list[ColissimoFrPickupSite]

    @classmethod
    def from_params(cls, results):
        return cls.model_construct(
            quality=results["qualiteReponse"],
            sites=[
                ColissimoFrPickupSite.from_params(site)
                for site in results["listePointRetraitAcheminement"]
            ],
        )


class ColissimoFrPickupSiteGetOutput(PickupSiteGetOutput):
    site: ColissimoFrPickupSite

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            site=ColissimoFrPickupSite.from_params(result["pointRetraitAcheminement"])
            if result["pointRetraitAcheminement"]
            else None
        )


class ColissimoFrPackingSlipInput(PackingSlipInput):
    auth: ColissimoFrAuth

    def params(self):
        params = {
            **self.auth.params(),
        }
        if self.parcels_numbers:
            params["generateBordereauParcelNumberList"] = {
                "parcelsNumbers": self.parcels_numbers
            }

        return params


class ColissimoFrPackingSlip(PackingSlip):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            number=result["bordereauNumber"],
            published_datetime=(
                datetime.fromtimestamp(result["publishingDate"] / 1000)
                if result["publishingDate"]
                else None
            ),
            number_of_parcels=result["numberOfParcels"],
            client=PackingSlipClient(
                number=result["clientNumber"],
                address=result["address"],
                company=result["company"],
            ),
            site_pch=PackingSlipSupportSite(
                code=result["codeSitePCH"], name=result["nameSitePCH"]
            ),
        )


class ColissimoFrPackingSlipOutput(PackingSlipOutput):
    packing_slip: ColissimoFrPackingSlip
    annexes: list[Label] = []

    @classmethod
    def from_params(cls, results):
        return cls.model_construct(
            packing_slip=ColissimoFrPackingSlip.from_params(
                results["<jsonInfos>"]["bordereauHeader"]
            ),
            annexes=[
                ColissimoFrLabel.from_params(data, annex.strip("<>"), Format.PDF.value)
                for annex, data in results.items()
                if annex not in ["<jsonInfos>"]
            ],
        )


class Lang(str, Enum):
    fr_FR = "fr_FR"
    en_GB = "en_GB"
    es_ES = "es_ES"
    de_DE = "de_DE"
    it_IT = "it_IT"


class DocumentType(str, Enum):
    certificate_of_origin = "CERTIFICATE_OF_ORIGIN"  # Certificat d'origine
    export_license = "EXPORT_LICENSE"  # Licence d'exportation
    commercial_invoice = "COMMERCIAL_INVOICE"  # Facture du colis
    other = "OTHER"  # Autre


class ColissimoFrDocumentAuth(ColissimoFrAuth):
    def params(self):
        credential = {}
        if self.apiKey:
            credential["apiKey"] = self.apiKey
        else:
            credential["login"] = self.login
            credential["password"] = self.password

        return {
            "credential": credential,
        }


class ColissimoFrDocumentService(DocumentService):
    language: Lang = Lang.fr_FR

    def params(self):
        return {
            "lang": self.language.value,
            "cab": self.parcel_number,
        }


class ColissimoFrGetDocumentsInput(GetDocumentsInput):
    auth: ColissimoFrDocumentAuth
    service: ColissimoFrDocumentService

    def params(self):
        return {
            **self.auth.params(),
            **self.service.params(),
        }


class ColissimoFrGetDocumentService(GetDocumentService, ColissimoFrDocumentService):
    uuid: str | None = None

    def params(self):
        return {
            **super().params(),
            "path": self.document_id,
            "uuid": self.uuid,
        }


class ColissimoFrGetDocumentInput(GetDocumentInput):
    auth: ColissimoFrDocumentAuth
    service: ColissimoFrGetDocumentService

    def params(self):
        return {
            **self.auth.params(),
            **self.service.params(),
        }


class ColissimoFrCreateUpdateDocumentService(
    CreateUpdateDocumentService, ColissimoFrDocumentService
):
    document_type: DocumentType
    customerId: str
    parcel_number: str
    parcel_number_list: str | None = None

    def params(self):
        return {
            **super().params(),
            "documentType": self.document_type.value,
            "accountNumber": self.customerId,
            "parcelNumber": self.parcel_number,
            "parcelNumberList": self.parcel_number_list,
            "filename": Path(self.document_path).name,
        }


class ColissimoFrCreateUpdateDocumentInput(CreateUpdateDocumentInput):
    auth: ColissimoFrDocumentAuth
    service: ColissimoFrCreateUpdateDocumentService

    def params(self):
        return {
            **self.auth.params(),
            **self.service.params(),
        }


class ColissimoFrDocumentOutput(DocumentOutput):
    file: str

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            file=b64encode(result).decode("utf-8"),
        )


class ColissimoFrDocument(BaseModel):
    url: str
    code: str | None = None
    date: datetime | None = None
    site_code: str | None = None
    site_name: str | None = None
    site_type: str | None = None
    document_type: str
    document_path: str | None = None
    uuid: str | None = None
    parcel_number: str | None = None

    @classmethod
    def from_params(cls, result):
        def fromisoformat(value):
            """Compat python < 3.11."""
            # Remove after dropping support for python < 3.11
            if "+" in value:
                time = value.split("+", 1)[1]
                if ":" not in time:
                    time = time[:2] + ":" + time[2:]
                    value = value.split("+", 1)[0] + "+" + time

            return datetime.fromisoformat(value)

        return cls.model_construct(
            url=result["url"],
            code=result["eventCode"],
            date=fromisoformat(result["eventDate"]),
            site_code=result["eventSiteCode"],
            site_name=result["eventSiteName"],
            site_type=result["eventSiteType"],
            document_type=result["documentType"],
            document_path=result["path"],
            uuid=result["uuid"],
            parcel_number=result["cab"],
        )


class ColissimoFrDocumentsOutput(DocumentOutput):
    documents: list[ColissimoFrDocument]

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            documents=[
                ColissimoFrDocument.from_params(doc) for doc in result["documents"]
            ],
        )


class ColissimoFrCreateUpdateDocumentOutput(DocumentOutput):
    document_id: str

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            document_id=result["documentId"],
        )
