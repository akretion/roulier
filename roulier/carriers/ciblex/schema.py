# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ...helpers import prefix, suffix, none_as_empty, unaccent
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


class CiblexAuth(Auth):
    login: str
    password: str

    def params(self):
        return {
            "USER_COMPTE": self.login,
            "USER_PASSWORD": self.password,
            "lang": "fr",
            "LOGIN": "Connexion sécurisée",
        }


class CiblexService(Service):
    customerId: str
    product: str
    imperative_time: str | None = None  # 08:00, 09:00
    opt_ssm: bool | None = None

    def params(self):
        return {
            "expediteur": self.customerId,
            "prestation": self.product,
            "date_cmd": self.shippingDate.strftime("%d/%m/%Y"),
            "imperatif": self.imperative_time,
            "opt_ssm": self.opt_ssm,
        }


class CiblexParcel(Parcel):
    reference2: str | None = None
    reference3: str | None = None
    delivery_versus: float | None = None
    check_payable_to: str | None = None
    # ad_valorem_types: 1 : standand, 2 : sensible, 4 : international
    ad_valorem_type: int | None = None
    ad_valorem: float | None = None
    ad_valorem_agreed: bool | None = None

    def params(self):
        return {
            "poids": self.weight,
            "ref1": self.reference,
            "ref2": self.reference2,
            "ref3": self.reference3,
            "cpa": self.delivery_versus,
            "ordre_chq": self.check_payable_to,
            "opt_adv": self.ad_valorem_type,
            "adv": self.ad_valorem,
            "adv_cond": self.ad_valorem_agreed,
        }


class CiblexAddress(Address):
    zip: str
    city: str
    country: str  # FR ou MC, enum?
    street3: str | None = None
    street4: str | None = None

    def params(self):
        return {
            "raison": ", ".join([part for part in (self.name, self.company) if part]),
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

    def params(self):
        return unaccent(
            none_as_empty(
                {
                    "module": "cmdsai",
                    "commande": None,
                    **self.service.params(),
                    **prefix(self.from_address.params(), "exp_"),
                    **prefix(self.to_address.params(), "dest_"),
                    "nb_colis": len(self.parcels),
                    **{
                        k: v
                        for i, parcel in enumerate(self.parcels)
                        for k, v in suffix(parcel.params(), f"_{i+1}").items()
                    },
                }
            )
        )


class CiblexTracking(Tracking):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            number=result["tracking"],
            url=(
                "https://secure.extranet.ciblex.fr/extranet/client/"
                "corps.php?module=colis&colis=%s" % result["tracking"]
            ),
        )


class CiblexLabel(Label):
    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            data=result["label"].decode("utf-8"),
            name="label",
            type=result["format"],
        )


class CiblexParcelLabel(ParcelLabel):
    id: str
    label: CiblexLabel | None = None
    tracking: CiblexTracking | None = None

    @classmethod
    def from_params(cls, result):
        return cls.model_construct(
            id=result["id"],
            reference=result["reference"],
            label=CiblexLabel.from_params(result),
            tracking=CiblexTracking.from_params(result),
        )


class CiblexLabelOutput(LabelOutput):
    parcels: list[CiblexParcelLabel]

    @classmethod
    def from_params(cls, results):
        return cls.model_construct(
            parcels=[CiblexParcelLabel.from_params(result) for result in results],
        )
