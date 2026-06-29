"""Transform roulier input into a Mondial Relay Connect XML request."""

import logging

from lxml import etree

from roulier.codec import Encoder

from .constants import NS_REQUEST, VERSION_API

_logger = logging.getLogger(__name__)

# Sequence of the <Address> children, conforming to the request XSD.
# Each tuple is (xml_tag, roulier_address_field). AddressAdd1 carries the name and
# is the only mandatory address field for Mondial Relay.
_ADDRESS_FIELDS = (
    ("Title", "title"),
    ("Firstname", "firstname"),
    ("Lastname", "lastname"),
    ("Streetname", "street1"),
    ("HouseNo", "houseNo"),
    ("CountryCode", "country"),
    ("PostCode", "zip"),
    ("City", "city"),
    ("AddressAdd1", "name"),
    ("AddressAdd2", "company"),
    ("AddressAdd3", "street2"),
    ("PhoneNo", "phone"),
    ("MobileNo", "mobile"),
    ("Email", "email"),
)


class MondialRelayConnectEncoder(Encoder):
    def transform_input_to_carrier_webservice(self, data):
        service = data["service"]
        parcels = data["parcels"]

        root = etree.Element(
            "{%s}ShipmentCreationRequest" % NS_REQUEST,
            nsmap={
                None: NS_REQUEST,
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsd": "http://www.w3.org/2001/XMLSchema",
            },
        )

        self._add_context(root, data)
        self._add_output_options(root, service)

        shipments = etree.SubElement(root, "ShipmentsList")
        shipment = etree.SubElement(shipments, "Shipment")
        self._add_shipment(shipment, data, service, parcels)

        body = etree.tostring(
            root, xml_declaration=True, encoding="utf-8", pretty_print=False
        )
        return {
            "body": body,
            "output_type": service["outputType"],
            "label_format": service["labelFormat"],
        }

    def _add_context(self, root, data):
        ctx = etree.SubElement(root, "Context")
        self._text(ctx, "Login", data["auth"]["login"])
        self._text(ctx, "Password", data["auth"]["password"])
        self._text(ctx, "CustomerId", data["service"]["customerId"])
        self._text(ctx, "Culture", data["service"]["culture"])
        self._text(ctx, "VersionAPI", VERSION_API)

    def _add_output_options(self, root, service):
        out = etree.SubElement(root, "OutputOptions")
        self._text(out, "OutputFormat", service["labelFormat"])
        self._text(out, "OutputType", service["outputType"])

    def _add_shipment(self, shipment, data, service, parcels):
        order_no = service["orderNo"] or service.get("reference1", "")
        customer_no = service["customerNo"] or service.get("reference2", "")
        if order_no:
            self._text(shipment, "OrderNo", order_no)
        if customer_no:
            self._text(shipment, "CustomerNo", customer_no)
        self._text(shipment, "ParcelCount", str(max(1, len(parcels))))

        delivery = etree.SubElement(shipment, "DeliveryMode")
        delivery.set("Mode", service["deliveryMode"])
        delivery.set("Location", service["deliveryLocation"])

        collection = etree.SubElement(shipment, "CollectionMode")
        collection.set("Mode", service["collectionMode"])
        collection.set("Location", service["collectionLocation"])

        # Mondial Relay Connect carries a single weight/dimensions block for the
        # shipment; ParcelCount above drives the number of printed labels.
        self._add_parcel(shipment, parcels[0])

        instruction = data["to_address"].get("delivery_instruction", "")
        if instruction:
            self._text(shipment, "DeliveryInstruction", instruction)

        sender = etree.SubElement(shipment, "Sender")
        self._add_address(sender, data.get("from_address", {}))
        recipient = etree.SubElement(shipment, "Recipient")
        self._add_address(recipient, data["to_address"])

    def _add_parcel(self, shipment, parcel):
        parcels_node = etree.SubElement(shipment, "Parcels")
        parcel_node = etree.SubElement(parcels_node, "Parcel")
        if parcel.get("content"):
            self._text(parcel_node, "Content", parcel["content"])

        weight = etree.SubElement(parcel_node, "Weight")
        grams = max(10, int(round(float(parcel["weight"]) * 1000)))
        weight.set("Value", str(grams))
        weight.set("Unit", "gr")

        for tag, field in (("Length", "length"), ("Width", "width"), ("Depth", "height")):
            value = parcel.get(field)
            if value:
                dim = etree.SubElement(parcel_node, tag)
                dim.set("Value", str(int(value)))
                dim.set("Unit", "cm")

    def _add_address(self, parent, address):
        addr = etree.SubElement(parent, "Address")
        for tag, field in _ADDRESS_FIELDS:
            # All tags are emitted, empty ones included (the API tolerates them and
            # the XSD expects the full sequence).
            self._text(addr, tag, address.get(field, ""))

    @staticmethod
    def _text(parent, tag, value):
        el = etree.SubElement(parent, tag)
        if value not in (None, ""):
            el.text = str(value)
        return el
