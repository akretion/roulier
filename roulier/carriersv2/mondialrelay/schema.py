# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from ..helpers import prefix, clean_empty, REMOVED
from ..schema import (
    Address,
    Auth,
    Label,
    LabelInput,
    LabelOutput,
    Parcel,
    ParcelLabel,
    PickupSite,
    PickupSiteInput,
    PickupSiteOutput,
    PickupSiteSearch,
    Service,
)
from .constants import SORTED_KEYS
from hashlib import md5


class MondialRelayAuth(Auth):
    login: str
    password: str

    def soap(self):
        return {
            "Enseigne": self.login,
        }

    def sign(self, parameters):
        m = md5()
        m.update(
            "".join(
                [
                    str(v)
                    for k in SORTED_KEYS
                    for v in [parameters.get(k)]
                    if v is not None
                ]
                + [self.password]
            ).encode(
                "iso-8859-1"
            )  # And not utf-8, yes the doc says otherwise
        )
        parameters["Security"] = m.hexdigest().upper()
        return parameters


class MondialRelayService(Service):
    pickupMode: str
    cashOnDelivery: int = 0
    cashOnDeliveryCurrency: str = "EUR"
    price: int | None = None
    currency: str = "EUR"
    pickupCountry: str | None = None
    pickupSite: str | None = None
    shippingCountry: str | None = None
    shippingSite: str | None = None
    notice: bool | None = None
    takeBack: bool | None = None
    assemblyTime: int | None = None
    insurance: int | None = None
    text: str | None = None

    shippingDate: REMOVED

    def french_boolean(self, value):
        if value is None:
            return None
        return "O" if value else "N"

    def soap(self):
        return {
            "ModeCol": self.pickupMode,
            "ModeLiv": self.product,
            "NDossier": self.shippingId,
            "NClient": self.customerId,
            "CRT_Valeur": self.cashOnDelivery,
            "CRT_Devise": self.cashOnDeliveryCurrency,
            "Exp_Valeur": self.price,
            "Exp_Devise": self.currency,
            "COL_Rel_Pays": self.pickupCountry,
            "COL_Rel": self.pickupSite,
            "LIV_Rel_Pays": self.shippingCountry,
            "LIV_Rel": self.shippingSite,
            "TAvisage": self.french_boolean(self.notice),
            "TReprise": self.french_boolean(self.takeBack),
            "Montage": self.assemblyTime,
            # "TRDV": self.TRDV, Unused
            "Assurance": self.insurance,
            "Instructions": self.instructions,
            "Texte": self.text,
        }


class MondialRelayParcel(Parcel):
    length: int | None = None
    height: str | None = None
    count: int = 1

    def soap(self):
        return {
            "Poids": int(self.weight * 1000),
            "Longueur": self.length,
            "Taille": self.height,
            "NbColis": self.count,
        }


class MondialRelayAddress(Address):
    lang: str
    country: str
    zip: str
    city: str
    street1: str
    phone2: str | None = None

    def soap(self):
        return {
            "Langage": self.lang,
            "Ad1": self.name,
            "Ad2": self.company,
            "Ad3": self.street1,
            "Ad4": self.street2,
            "Ville": self.city,
            "CP": self.zip,
            "Pays": self.country,
            "Tel1": self.phone,
            "Tel2": self.phone2,
            "Mail": self.email,
        }


class MondialRelayFromAddress(MondialRelayAddress):
    phone: str


class MondialRelayLabelInput(LabelInput):
    auth: MondialRelayAuth
    service: MondialRelayService
    parcels: list[MondialRelayParcel]
    from_address: MondialRelayFromAddress
    to_address: MondialRelayAddress

    def soap(self):
        return self.auth.sign(
            clean_empty(
                {
                    **self.auth.soap(),
                    **self.service.soap(),
                    **self.parcels[0].soap(),
                    **prefix(self.from_address.soap(), "Expe_"),
                    **prefix(self.to_address.soap(), "Dest_"),
                }
            )
        )


class MondialRelayPickupSiteSearch(PickupSiteSearch):
    id: int | None = None
    weight: float | None = None
    action: str | None = None
    delay: int | None = None
    searchRadius: int | None = None
    actionType: str | None = None
    resultsCount: int | None = None

    def soap(self):
        return clean_empty(
            {
                "Pays": self.country,
                "NumPointRelais": self.id,
                "CP": self.zip,
                "Latitude": self.lat,
                "Longitude": self.lng,
                "Poids": self.weight,
                "Action": self.action,
                "DelaiEnvoi": self.delay,
                "RayonRecherche": self.searchRadius,
                "TypeActivite": self.actionType,
                "NombreResultats": self.resultsCount,
            }
        )


class MondialRelayPickupSiteInput(PickupSiteInput):
    auth: MondialRelayAuth
    search: MondialRelayPickupSiteSearch

    def soap(self):
        return self.auth.sign(
            clean_empty(
                {
                    **self.auth.soap(),
                    **self.search.soap(),
                }
            )
        )


class MondialRelayLabel(Label):
    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(
            data=f"https://www.mondialrelay.com{result['URL_Etiquette']}",
            name="label_url",
            type="url",
        )


class MondialRelayParcelLabel(ParcelLabel):
    label: MondialRelayLabel | None = None

    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(
            id=int(result["ExpeditionNum"]),
            label=MondialRelayLabel.from_soap(result),
        )


class MondialRelayLabelOutput(LabelOutput):
    parcels: list[MondialRelayParcelLabel]

    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(parcels=[MondialRelayParcelLabel.from_soap(result)])


class MondialRelayPickupSite(PickupSite):
    actionType: str
    hours: dict
    url_pic: str
    url_map: str

    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(
            id=result["Num"],
            name="\n".join(
                [part for part in [result["LgAdr1"], result["LgAdr2"]] if part]
            ),
            street="\n".join(
                [part for part in [result["LgAdr3"], result["LgAdr4"]] if part]
            ),
            zip=result["CP"],
            city=result["Ville"],
            country=result["Pays"],
            lat=result["Latitude"],
            lng=result["Longitude"],
            actionType=result["TypeActivite"],
            hours={
                "monday": result["Horaires_Lundi"],
                "tuesday": result["Horaires_Mardi"],
                "wednesday": result["Horaires_Mercredi"],
                "thursday": result["Horaires_Jeudi"],
                "friday": result["Horaires_Vendredi"],
                "saturday": result["Horaires_Samedi"],
                "sunday": result["Horaires_Dimanche"],
            },
            url_pic=result["URL_Photo"],
            url_map=result["URL_Plan"],
        )


class MondialRelayPickupSiteOutput(PickupSiteOutput):
    sites: list[MondialRelayPickupSite]

    @classmethod
    def from_soap(cls, result):
        return cls.model_construct(
            sites=[
                MondialRelayPickupSite.from_soap(site)
                for site in result["PointsRelais"]["PointRelais_Details"]
            ]
        )
