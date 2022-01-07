"""Transform input to laposte compatible xml."""

from jinja2 import Environment, PackageLoader
import logging

from roulier.codec import Encoder
from roulier.exception import InvalidApiInput

from .constants import SERVICE_FDS
from .constants import SERVICE_SHD
from .constants import SERVICE_SRS

_logger = logging.getLogger(__name__)


class GlsEuEncoderBase(Encoder):
    def transform_input_to_carrier_webservice(self, data):
        """
        Transforms standard roulier input into gls specific request data
        """
        body = {
            "shipperId": "%s %s"
            % (data["service"]["customerId"], data["service"]["agencyId"]),
            "shipmentDate": "%s" % data["service"]["shippingDate"],
            "labelFormat": data["service"]["labelFormat"],
            "labelSize": data["service"]["labelSize"],
        }
        if data["service"].get("incoterm"):
            body["incoterm"] = data["service"]["incoterm"]
        body["addresses"] = self._transforms_addresses(data, body)
        if "return" in body["addresses"] and data.get("return_weight"):
            body["returns"] = {"weight": "%.2f" % data["return_weight"]}
        references = [
            ref.strip()
            for ref in (
                data.get("reference1", ""),
                data.get("reference2", ""),
                data.get("reference3", ""),
            )
            if ref.strip()
        ]
        if references:
            body["references"] = references[:2]
        if data.get("returns") and "return" in body["addresses"]:
            body["returns"] = [
                {"weight": "%.2f" % ret["weight"]}
                for ret in data.get("returns")
                if ret.get("weight")
            ]
        body["parcels"] = self._transforms_parcels(data, body)
        return {
            "body": body,
            "auth": data["auth"],
            "language": data["service"].get("language", "en"),
        }

    def _transforms_addresses(self, data, body):
        """
        Transforms standard roulier addresses input into gls specific request data
        """
        addresses = {}
        available_addr = (("to_address", "delivery"),)
        if data.get("from_address"):
            available_addr += (("from_address", "alternativeShipper"),)
        if data.get("return_address"):
            available_addr += (("return_address", "return"),)
        if data.get("pickup_address"):
            available_addr += (("pickup_address", "pickup"),)

        addr_req_fields = (
            ("name", "name1"),  # Raison sociale ou nom destinataire
            (
                "street1",
                "street1",
            ),  # Adresse principale => si adresse sur plusieurs lignes, renseigner le nom de la rue ICI
            (
                "country",
                "country",
            ),  # deux lettres du code pays -> ISO 3166-1-alpha-2 (ex: "FR")
            (
                "zip",
                "zipCode",
            ),  # code postal (cas particulier: province pour l'Irlande)
            ("city", "city"),  # Ville
        )
        addr_opt_fields = (
            (
                "id",
                "id",
            ),  # Identifiant adresse (référence utilisable pour recherche track&trace sur notre site YourGLS)
            ("street2", "name2"),  # Complément d'adresse
            ("street3", "name3"),  # Complément d'adresse
            (
                "blockNo1",
                "blockNo1",
            ),  # Numéro de la maison ou de l'immeuble dans la rue - apparait à la suite du champ "Street1" sur l'étiquette - Ne renseigner QUE si non présent dans les informations mises en "Street1"
            ("contact", "contact"),  # Nom d'un contact
            ("phone", "phone"),  # Numéro de téléphone : obligatoire si pas de mobile
            (
                "mobile",
                "mobile",
            ),  # Numéro de téléphone mobile : obligatoire si pas de fixe
            ("email", "email"),  # Adresse E-mail - /!\Obligatoire en BtoC
        )
        for from_addr, to_addr in available_addr:
            addr = data.get(from_addr)
            if not addr:
                continue
            # if the company address field is set, then the name is actually the contact
            if addr["company"] and addr["name"]:
                addr["contact"] = addr["name"]
                addr["name"] = addr["company"]
            addresses[to_addr] = dict(
                (to_field, addr[from_field]) for from_field, to_field in addr_req_fields
            )
            addresses[to_addr]["country"] = addresses[to_addr]["country"].upper()
            addresses[to_addr].update(
                dict(
                    (to_field, addr[from_field])
                    for from_field, to_field in addr_opt_fields
                    if addr.get(from_field)
                )
            )
            if addresses[to_addr]["country"] == "IR" and addr.get("province"):
                addresses[to_addr]["province"] = addr.get("province")
        return addresses

    def _transforms_parcels(self, data, body):
        """
        Transforms standard roulier parcels input into gls specific request data
        """
        parcels = []
        global_sevice = (
            self._set_service(data["service"], body)
            if "product" in data["service"]
            else None
        )
        for p in data["parcels"]:
            parcel = {"weight": "%.2f" % p["weight"]}
            refs = []
            if p.get("reference"):
                refs.append(p["reference"])
            if p.get("reference2"):
                refs.append(p["reference2"])
            if refs:
                parcel["references"] = refs
            if p.get("comment"):
                parcel["comment"] = p["comment"]
            if "services" in p:
                services = []
                for subdata in p["services"]:
                    service = self._set_service(subdata, body)
                    if service:
                        services.append(service)
                if global_sevice:
                    services.append(global_sevice)
                if services:
                    parcel["services"] = services
            parcels.append(parcel)
        return parcels

    def _set_service(self, subdata, body):
        service_name = subdata.get("product")
        if service_name not in (SERVICE_FDS, SERVICE_SHD, SERVICE_SRS):
            return  # service must only be included fot those three ones
        service = {"name": service_name}
        if service_name == SERVICE_SHD:
            pickup_id = subdata.get("pickupLocationId")
            service["infos"] = [
                {
                    "name": "parcelshopid" if pickup_id else "directshop",
                    "value": pickup_id or "Y",
                }
            ]
        elif service_name == SERVICE_SRS and "pickup" in body["addresses"]:
            service["infos"] = [{"name": "returnonly", "value": "Y"}]
        return service


class GlsEuEncoder(GlsEuEncoderBase):
    """Transform input to laposte compatible xml."""

    pass
