"""Transform input to laposte compatible xml."""

import logging
import re
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput

from .constants import SERVICE_FDS, SERVICE_PandR, SERVICE_PandS
from .constants import SERVICE_SHD, SERVICES_KEYS
from .constants import SERVICE_SRS, SERVICE_STANDARD

_logger = logging.getLogger(__name__)


class GlsShipItEncoderBase(Encoder):
    def transform_input_to_carrier_webservice(self, data):
        """
        Transforms standard roulier input into gls specific request data
        """
        body = {
            "PrintingOptions": {
                "ReturnLabels": {
                    "LabelFormat": data["service"]["labelFormat"],
                    "TemplateSet": "NONE",
                },
            },
            "Shipment": {
                "Consignee": {},
                "Product": "PARCEL",
                "Shipper": {
                    "ContactID": data["service"]["contact_id"],
                },
                "ShippingDate": "%s" % data["service"]["shippingDate"],
            },
        }
        service = data["service"].get("product")
        if service and service != SERVICE_STANDARD:
            service_key = SERVICES_KEYS[service]
            service = {"ServiceName": service}
            returns = data.get("returns")
            if returns:
                service["NumberOfLabels"] = len(returns)
            pickup_id = data["service"].get("pickupLocationId")
            if pickup_id:
                service["ParcelShopID"] = pickup_id
            pickup_date = data["service"].get("pickupDate")
            if pickup_date:
                service["PickupDate"] = str(pickup_date)
            body["Shipment"]["Service"] = [{service_key: service}]
        if data.get("to_address"):
            body["Shipment"]["Consignee"]["Address"] = self._transforms_addr(
                data["to_address"]
            )
        elif data.get("pickup_address") and service["ServiceName"] == SERVICE_PandR:
            body["Shipment"]["Consignee"]["Address"] = self._transforms_addr(
                data["pickup_address"]
            )
        if (
            data.get("shipping_address")
            and service
            and service["ServiceName"] == SERVICE_PandS
        ):
            body["Shipment"]["Shipper"]["AlternativeShipperAddress"] = (
                self._transforms_addr(data["shipping_address"])
            )

        parcels = self._transforms_parcels(data, body)
        body["Shipment"]["ShipmentUnit"] = parcels
        body["Shipment"]["ShipmentReference"] = [
            p["ShipmentUnitReference"] for p in parcels if "ShipmentUnitReference" in p
        ]
        if data["service"].get("incoterm"):
            body["Shipment"]["IncotermCode"] = data["service"]["incoterm"]
        return {
            "body": body,
            "auth": data["auth"],
            "language": data["service"].get("language", "en"),
        }

    def _transforms_addr(self, data):
        """
        Transforms standard roulier addresses input into gls specific request data
        """
        if not data:
            return {}
        formated_addr = {}
        # if the company address field is set, then the name is actually the contact
        if data["company"] and data["name"]:
            formated_addr["ContactPerson"] = data["name"]
            formated_addr["Name2"] = data["name"]
            formated_addr["Name1"] = data["company"]
        else:
            formated_addr["Name1"] = data["name"]
        # if data.get("contact_id"):
        #     formated_addr["contact"] = data["contact_id"]
        formated_addr["CountryCode"] = data["country"].upper()

        if data.get("province"):
            formated_addr["Province"] = data.get("province")

        if data["street1"]:
            groups = re.match(r"^((\d*)(\s(bis)|(ter))?)\s.*", data["street1"])
            if groups:
                number = groups.group(1)
                formated_addr["StreetNumber"] = number
                formated_addr["Street"] = data["street1"].replace(number, "")
            else:
                formated_addr["Street"] = data["street1"]
        formated_addr["City"] = data["city"]
        if data["zip"]:
            # warning: it's not a mistake, it's really ZIPCode and not ZipCode as other fields...
            formated_addr["ZIPCode"] = data["zip"]
            # formated_addr["zip"] = data["zip"]
            # formated_addr["Zip"] = data["zip"]
            # formated_addr["zipcode"] = data["zip"]
            # formated_addr["zipCode"] = data["zip"]
            # formated_addr["ZipCode"] = data["zip"]
            # formated_addr["PostalCode"] = data["zip"]
            # formated_addr["postalCode"] = data["zip"]
            # formated_addr["City"] += " " + data["city"]
        if data["phone"]:
            formated_addr["MobilePhoneNumber"] = data["phone"]
        if data["email"]:
            # warning: it's not a mistake, it's really eMail and not Email as other fields...
            formated_addr["eMail"] = data["email"]
        return formated_addr

    def _transforms_parcels(self, data, body):
        """
        Transforms standard roulier parcels input into gls specific request data
        """
        parcels = []
        for p in data["parcels"]:
            parcel = {
                "Weight": "%.2f" % p["weight"],
            }

            refs = []
            if p.get("reference"):
                parcel["ShipmentUnitReference"] = p["reference"]
            elif p.get("reference2"):
                parcel["ShipmentUnitReference"] = p["reference2"]
            if p.get("comment"):
                parcel["Note1"] = p["comment"]
            parcels.append(parcel)
        return parcels


class GlsShipItEncoder(GlsShipItEncoderBase):
    pass
