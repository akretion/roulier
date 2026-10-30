# Copyright 2026 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator

from ...helpers import filter_empty, REMOVED
from ...schema import (
    Address,
    Label,
    LabelInput,
    LabelOutput,
    Parcel,
    ParcelLabel,
    PickupSite,
    PickupSiteGetOutput,
    PickupSiteOpeningHours,
    PickupSiteOpeningSlot,
    PickupSiteSearch,
    PickupSiteSearchInput,
    PickupSiteSearchOutput,
    Service,
    ToAddress,
    Tracking,
)


MIME_TYPES = {
    "PDF": "application/pdf",
    "ZPL": "application/zpl",
    "PNG": "image/png",
}

DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

# Countries where the house number is written before the street name
NUMBER_FIRST_COUNTRIES = {"FR", "LU", "GB", "IE"}


class SendcloudService(Service):
    product: str  # Shipping option code, ex: "colissimo:home/signature"
    contractId: int | None = None
    pickupLocationId: str | None = None
    senderAddressId: int | None = None
    labelFormat: Literal["PDF", "ZPL", "PNG"] = "ZPL"
    dpi: int | None = None

    shippingDate: REMOVED

    @property
    def mime_type(self):
        return MIME_TYPES[self.labelFormat]

    def label_details(self):
        return filter_empty(
            {
                "mime_type": self.mime_type,
                "dpi": self.dpi,
            }
        )

    def to_request(self):
        return filter_empty(
            {
                "ship_with": {
                    "type": "shipping_option_code",
                    "properties": {
                        "shipping_option_code": self.product,
                        "contract_id": self.contractId,
                    },
                },
                "to_service_point": (
                    {"id": self.pickupLocationId} if self.pickupLocationId else None
                ),
                "order_number": self.reference1,
                "reference": self.reference2,
                "external_reference_id": self.shippingId,
                "label_details": self.label_details(),
            }
        )


class SendcloudParcelItem(BaseModel):
    description: str
    weight: float
    quantity: int = 1
    price: float | None = None
    currency: str = "EUR"
    hsCode: str | None = None
    originCountry: str | None = None
    sku: str | None = None

    def to_request(self):
        return filter_empty(
            {
                "description": self.description,
                "quantity": self.quantity,
                "weight": {"value": f"{self.weight:.3f}", "unit": "kg"},
                "price": (
                    {"value": f"{self.price:.2f}", "currency": self.currency}
                    if self.price is not None
                    else None
                ),
                "hs_code": self.hsCode,
                "origin_country": self.originCountry,
                "sku": self.sku,
            }
        )


class SendcloudParcel(Parcel):
    # Dimensions in cm
    length: float | None = None
    width: float | None = None
    height: float | None = None
    items: list[SendcloudParcelItem] = []

    def to_request(self):
        dimensions = None
        if self.length and self.width and self.height:
            dimensions = {
                "length": str(self.length),
                "width": str(self.width),
                "height": str(self.height),
                "unit": "cm",
            }
        return filter_empty(
            {
                "weight": {"value": f"{self.weight:.3f}", "unit": "kg"},
                "dimensions": dimensions,
                "parcel_items": [item.to_request() for item in self.items] or None,
            }
        )


def address_to_request(address: Address):
    return filter_empty(
        {
            "name": address.name,
            "company_name": address.company,
            "address_line_1": address.street1,
            "address_line_2": address.street2,
            "postal_code": address.zip,
            "city": address.city,
            "country_code": address.country,
            "phone_number": address.phone,
            "email": address.email,
        }
    )


class SendcloudLabelInput(LabelInput):
    service: SendcloudService
    parcels: list[SendcloudParcel]
    # Not required when service.senderAddressId is given
    from_address: Address | None = None
    to_address: ToAddress

    @model_validator(mode="after")
    def check_from_address(self):
        if not self.service.senderAddressId and not self.from_address:
            raise ValueError("from_address or service.senderAddressId is required")
        return self

    def to_request(self):
        if self.service.senderAddressId:
            from_address = {"sender_address_id": self.service.senderAddressId}
        else:
            from_address = address_to_request(self.from_address)
        return {
            **self.service.to_request(),
            "from_address": from_address,
            "to_address": address_to_request(self.to_address),
            "parcels": [parcel.to_request() for parcel in self.parcels],
        }


class SendcloudPickupSiteSearch(PickupSiteSearch):
    zip: str | None = None
    lat: float | None = None
    lng: float | None = None
    carrierCode: list[str] | None = None
    radius: int | None = None  # In meters, 100 to 50000
    limit: int | None = None

    @model_validator(mode="after")
    def check_location(self):
        if not (self.zip or self.city or self.street) and (
            self.lat is None or self.lng is None
        ):
            raise ValueError("zip, city, street or lat/lng is required")
        return self

    def to_params(self):
        params = {
            "country_code": self.country,
            "radius": self.radius,
            "limit": self.limit,
        }
        if self.carrierCode:
            params["carrier_code"] = self.carrierCode
        else:
            params["use_integration_carriers"] = "true"
        if self.lat is not None and self.lng is not None:
            params.update({"latitude": self.lat, "longitude": self.lng})
        elif self.zip:
            params.update(
                {
                    "address_street": self.street,
                    "address_postal_code": self.zip,
                    "address_city": self.city,
                }
            )
        else:
            # address_street requires the postal code: geocoded free text
            params["address"] = ", ".join(
                part for part in (self.street, self.city) if part
            )
        return filter_empty(params)


class SendcloudPickupSiteSearchInput(PickupSiteSearchInput):
    search: SendcloudPickupSiteSearch


class SendcloudLabel(Label):
    @classmethod
    def from_response(cls, data, format):
        return cls.model_construct(
            data=data,
            name=f"{format} Label",
            type=format,
        )


class SendcloudTracking(Tracking):
    @classmethod
    def from_response(cls, result):
        return cls.model_construct(
            number=result.get("tracking_number"),
            url=result.get("tracking_url"),
        )


class SendcloudParcelLabel(ParcelLabel):
    label: SendcloudLabel | None = None

    @classmethod
    def from_response(cls, result, reference, label_data, format):
        return cls.model_construct(
            id=result["id"],
            reference=reference,
            tracking=SendcloudTracking.from_response(result),
            label=(
                SendcloudLabel.from_response(label_data, format) if label_data else None
            ),
        )


class SendcloudLabelOutput(LabelOutput):
    parcels: list[SendcloudParcelLabel]

    @classmethod
    def from_response(cls, input, parcels, labels):
        """`parcels` are the response parcels, in the same order as the input
        parcels, and `labels` the matching base64 encoded label files."""
        return cls.model_construct(
            parcels=[
                SendcloudParcelLabel.from_response(
                    parcel,
                    input_parcel.reference,
                    label,
                    input.service.labelFormat,
                )
                for parcel, input_parcel, label in zip(parcels, input.parcels, labels)
            ]
        )


class SendcloudPickupSiteOpeningSlot(PickupSiteOpeningSlot):
    @classmethod
    def from_response(cls, slot):
        return cls.model_construct(
            start=datetime.strptime(slot["start_time"], "%H:%M").time(),
            end=datetime.strptime(slot["end_time"], "%H:%M").time(),
        )


class SendcloudPickupSiteOpeningHours(PickupSiteOpeningHours):
    @classmethod
    def from_response(cls, opening_times):
        opening_times = opening_times or {}
        return cls.model_construct(
            **{
                day: [
                    SendcloudPickupSiteOpeningSlot.from_response(slot)
                    for slot in opening_times.get(day) or []
                ]
                for day in DAYS
            }
        )


class SendcloudPickupSite(PickupSite):
    carrier: str | None = None
    carrierServicePointId: str | None = None
    shopType: str | None = None
    distance: int | None = None

    @classmethod
    def from_response(cls, result):
        address = result.get("address") or {}
        position = result.get("position") or {}
        street_parts = (address.get("street"), address.get("house_number"))
        if address.get("country_code") in NUMBER_FIRST_COUNTRIES:
            street_parts = street_parts[::-1]
        return cls.model_construct(
            id=str(result["id"]),
            name=result["name"],
            street=" ".join(part for part in street_parts if part),
            zip=address.get("postal_code"),
            city=address.get("city"),
            country=address.get("country_code"),
            lat=str(position.get("latitude")),
            lng=str(position.get("longitude")),
            hours=SendcloudPickupSiteOpeningHours.from_response(
                result.get("opening_times")
            ),
            carrier=(result.get("carrier") or {}).get("code"),
            carrierServicePointId=result.get("carrier_service_point_id"),
            shopType=result.get("general_shop_type"),
            distance=result.get("distance"),
        )


class SendcloudPickupSiteSearchOutput(PickupSiteSearchOutput):
    sites: list[SendcloudPickupSite]

    @classmethod
    def from_response(cls, result):
        return cls.model_construct(
            sites=[
                SendcloudPickupSite.from_response(site)
                for site in result["data"]["results"]
                if not site.get("is_expired")
            ]
        )


class SendcloudPickupSiteGetOutput(PickupSiteGetOutput):
    site: SendcloudPickupSite | None = None

    @classmethod
    def from_response(cls, result):
        site = result.get("data")
        return cls.model_construct(
            site=SendcloudPickupSite.from_response(site) if site else None
        )
