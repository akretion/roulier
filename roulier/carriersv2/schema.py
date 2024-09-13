# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from pydantic import BaseModel


class Auth(BaseModel):
    login: str | None = None
    password: str | None = None
    isTest: bool = False


class Service(BaseModel):
    product: str | None = None
    agencyId: str | None = None
    customerId: str | None = None
    shippingId: str | None = None
    shippingDate: date
    reference1: str | None = None
    reference2: str | None = None
    reference3: str | None = None
    labelFormat: str | None = None
    instructions: str | None = None


class Parcel(BaseModel):
    weight: float
    reference: str | None = None


class Address(BaseModel):
    company: str | None = None
    name: str
    street1: str | None = None
    street2: str | None = None
    city: str | None = None
    country: str | None = None
    zip: str | None = None
    phone: str | None = None
    email: str | None = None


class ToAddress(Address):
    street1: str
    country: str
    city: str
    zip: str
    delivery_instructions: str | None = None


class LabelInput(BaseModel):
    auth: Auth
    service: Service
    parcels: list[Parcel]
    from_address: Address
    to_address: ToAddress


class PickupSiteSearch(BaseModel):
    country: str
    city: str | None = None
    zip: str
    lat: float | None = None
    lng: float | None = None


class PickupSiteInput(BaseModel):
    auth: Auth
    search: PickupSiteSearch


class Tracking(BaseModel):
    number: str
    url: str | None = None
    partner: str | None = None


class Label(BaseModel):
    data: str
    name: str
    type: str


class ParcelLabel(BaseModel):
    id: int
    reference: str | None = None
    tracking: Tracking | None = None
    label: Label | None = None


class LabelOutput(BaseModel):
    parcels: list[ParcelLabel]
    annexes: list[Label] = []


class PickupSite(BaseModel):
    id: int
    name: str
    street: str
    zip: str
    city: str
    country: str
    lat: str
    lng: str


class PickupSiteOutput(BaseModel):
    sites: list[PickupSite]
