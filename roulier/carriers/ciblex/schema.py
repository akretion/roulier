# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from enum import Enum

from pydantic import Field

from ...helpers import none_as_empty, prefix, suffix, unaccent
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
    EPL = "EPL"


class LabelType(Enum):
    STD = "STD"
    CUST = "CUST"


class CiblexAuth(Auth):
    login: str
    password: str

    def params(self):
        return {
            "i": self.login,
            "k": self.password,
        }


class CiblexService(Service):
    labelType: LabelType = LabelType.STD
    labelFormat: Format = Format.PDF
    thermicPrint: bool = True
    customerId: str
    product: str
    ssm: bool | None = None  # Saturday delivery
    logo: bool = False

    def french_boolean(self, value):
        if value is None:
            return None
        return "O" if value else "N"

    def params(self):
        return {
            "label_type": self.labelType.value,
            "output": self.labelFormat.value,
            "exp_code": self.customerId,
            "contrat": self.product,
            "date_ramasse": self.shippingDate.strftime("%d/%m/%Y")
            if self.shippingDate
            else None,
            "ssm": self.french_boolean(self.ssm),
            "logo": self.french_boolean(self.logo),
            "imp_therm_init": self.french_boolean(self.thermicPrint),
        }


class CiblexParcel(Parcel):
    reference2: str | None = None
    reference3: str | None = None
    delivery_versus: float | None = None

    def params(self):
        return {
            "poids": self.weight,
            "ref1": self.reference,
            "ref2": self.reference2,
            "ref3": self.reference3,
            "cpa": self.delivery_versus,
        }


class CiblexAddress(Address):
    zip: str
    city: str
    country: str | None
    street1: str = Field(max_length=35)
    street2: str | None = Field(max_length=35, default=None)
    street3: str | None = Field(max_length=35, default=None)
    street4: str | None = Field(max_length=35, default=None)

    def params(self):
        return {
            "nom": ", ".join([part for part in (self.name, self.company) if part]),
            "adr1": self.street1,
            "adr2": self.street2,
            "adr3": self.street3,
            "adr4": self.street4,
            "cp": self.zip,
            "ville": self.city,
            "pays": self.country,
            "tel": self.phone,
            "email": self.email,
        }


class CiblexLabelInput(LabelInput):
    auth: CiblexAuth
    service: CiblexService
    parcels: list[CiblexParcel]
    to_address: CiblexAddress
    from_address: CiblexAddress
    ret_address: CiblexAddress | None = None

    def params(self):
        return unaccent(
            none_as_empty(
                {
                    **self.auth.params(),
                    **self.service.params(),
                    **prefix(self.from_address.params(), "exp_"),
                    **prefix(self.to_address.params(), "dest_"),
                    **(
                        prefix(self.ret_address.params(), "ret_")
                        if self.ret_address
                        else {}
                    ),
                    **self.parcels[0].params(),
                }
            )
        )


class CiblexTracking(Tracking):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            number=result,
            url=(
                "https://secure.extranet.ciblex.fr/extranet/client/"
                "corps.php?module=colis&colis=%s" % result
            ),
        )


class CiblexLabel(Label):
    @classmethod
    def from_params(cls, result, type):
        return cls.model_construct(
            data=result,
            name="label",
            type=type,
        )


class CiblexParcelLabel(ParcelLabel):
    label: CiblexLabel | None = None
    tracking: CiblexTracking | None = None

    @classmethod
    def from_params(cls, result, input):

        return cls.model_construct(
            reference=input.parcels[0].reference,
            label=CiblexLabel.from_params(
                result["label"], input.service.labelFormat.value
            )
            if result.get("label") is not None
            else None,
            tracking=CiblexTracking.from_params(result["tracking"])
            if result.get("tracking") is not None
            else None,
        )


class CiblexLabelOutput(LabelOutput):
    parcels: list[CiblexParcelLabel]

    @classmethod
    def from_params(cls, results, input):
        return cls.model_construct(
            parcels=[
                CiblexParcelLabel.from_params(result, input) for result in results
            ],
        )
