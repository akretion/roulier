"""Implementation of the Mondial Relay Connect API schema."""

from roulier.api import ApiParcel

from .constants import (
    COLLECTION_MERCHANT,
    COLLECTION_MODES,
    DELIVERY_HOME,
    DELIVERY_MODES,
    OUTPUT_FORMATS,
    OUTPUT_PDF_URL,
    OUTPUT_TYPES,
)


class MondialRelayConnectApi(ApiParcel):
    """Expected input for the Mondial Relay Connect API (get_label)."""

    def _service(self):
        schema = super()._service()
        # Not used by this carrier: drop to avoid confusion in the public schema.
        for field in ("agencyId", "shippingId", "shippingDate", "product"):
            schema.pop(field, None)

        # CustomerId is mandatory in the request Context.
        schema["customerId"].update({"required": True, "empty": False})

        # Localisation sent in the Context (labels language / formatting).
        schema["culture"] = {"type": "string", "default": "fr-FR"}

        # Free data printed on the label (optional). Fall back to reference1/2.
        schema["orderNo"] = {"type": "string", "default": ""}
        schema["customerNo"] = {"type": "string", "default": ""}

        # Delivery / collection routing.
        schema["deliveryMode"] = {
            "type": "string",
            "default": DELIVERY_HOME,
            "allowed": DELIVERY_MODES,
        }
        schema["deliveryLocation"] = {"type": "string", "default": ""}
        schema["collectionMode"] = {
            "type": "string",
            "default": COLLECTION_MERCHANT,
            "allowed": COLLECTION_MODES,
        }
        schema["collectionLocation"] = {"type": "string", "default": ""}

        # Label output.
        schema["outputType"] = {
            "type": "string",
            "default": OUTPUT_PDF_URL,
            "allowed": OUTPUT_TYPES,
        }
        schema["labelFormat"].update(
            {
                "type": "string",
                "default": "10x15",
                "allowed": OUTPUT_FORMATS,
            }
        )
        return schema

    def _address(self):
        schema = super()._address()
        # Mondial Relay address extras (all optional, mapped 1:1 onto the XML).
        schema["title"] = {"type": "string", "default": ""}
        schema["firstname"] = {"type": "string", "default": ""}
        schema["lastname"] = {"type": "string", "default": ""}
        schema["houseNo"] = {"type": "string", "default": ""}
        schema["mobile"] = {"type": "string", "default": ""}
        return schema

    def _to_address(self):
        schema = super()._to_address()
        schema["country"].update({"required": True, "empty": False})
        schema["zip"].update({"required": True, "empty": False})
        schema["city"].update({"required": True, "empty": False})
        return schema

    def _parcel(self):
        schema = super()._parcel()
        # Parcel content printed on the label (<= 40 chars on the template).
        schema["content"] = {"type": "string", "default": ""}
        # Dimensions in centimeters (optional).
        schema["length"] = {"type": "integer", "default": None, "nullable": True}
        schema["width"] = {"type": "integer", "default": None, "nullable": True}
        schema["height"] = {"type": "integer", "default": None, "nullable": True}
        return schema

    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"].update({"required": True, "empty": False})
        return schema
