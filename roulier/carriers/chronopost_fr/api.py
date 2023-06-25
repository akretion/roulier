"""Implementation of Chronopost Api."""
from roulier.api import ApiParcel


CHRONOPOST_LABEL_FORMAT = {
    "PDF": "PDF",
    "PPR": "PDF",
    "SPD": "PDF",
    "THE": "PDF",
    "Z2D": "ZPL",
    "XML": "XML",
    "THEPSG": "PDF",
    "Z2DPSG": "ZPL",
}


class ChronopostFrApiParcel(ApiParcel):
    def _service(self):
        schema = super(ChronopostFrApiParcel, self)._service()
        schema["shippingId"].update(
            {"required": True, "empty": False, "type": "string", "maxlength": 35}
        )
        schema["customerId"].update(
            {"required": True, "empty": False, "type": "string", "maxlength": 35}
        )
        schema["product"].update(
            {"required": True, "empty": False, "type": "string", "maxlength": 2}
        )
        schema["labelFormat"].update(
            {
                "required": True,
                "empty": False,
                "type": "string",
                "allowed": list(CHRONOPOST_LABEL_FORMAT),
            }
        )
        schema["shippingHour"] = {
            "type": "integer",
            "maxlength": 2,
            "required": True,
            "empty": False,
        }
        schema["service"] = {
            "type": "string",
            "maxlength": 1,
            "default": "",
            "required": True,
            "empty": False,
            "allowed": ["0", "1", "6"],
        }
        return schema

    def _parcel(self):
        schema = super(ChronopostFrApiParcel, self)._parcel()
        schema["reference"].update({"maxlength": 15})
        schema["objectType"] = {
            "type": "string",
            "allowed": ["DOC", "MAR"],
            "required": True,
            "empty": False,
            "default": "",
        }
        schema["insuredValue"] = {"type": "integer"}
        schema["insuredCurrency"] = {"type": "string"}
        schema["codValue"] = {"type": "integer"}
        schema["codCurrency"] = {"type": "string"}
        schema["customsValue"] = {"type": "integer"}
        schema["customsCurrency"] = {"type": "string"}
        return schema

    def _address(self):
        schema = super(ChronopostFrApiParcel, self)._address()
        additional_fields = {
            "civility": {
                "type": "string",
                "allowed": ["E", "L", "M"],
            },
            "contact_name": {"type": "string", "maxlength": 100},
            "preAlert": {"type": "integer"},
        }
        schema["name"].update({"maxlength": 100})
        schema["street1"].update({"maxlength": 38})
        schema["street2"].update({"maxlength": 38})
        schema["country"].update({"maxlength": 2, "minlength": 2})
        schema["zip"].update({"maxlength": 9})
        schema["city"].update({"maxlength": 50})
        schema["email"].update({"maxlength": 50})
        schema["phone"].update({"maxlength": 17})
        schema.update(additional_fields)
        return schema

    def _to_address(self):
        schema = super(ChronopostFrApiParcel, self)._to_address()
        schema["preAlert"].update({"allowed": [0, 22]})
        return schema

    def _from_address(self):
        schema = super(ChronopostFrApiParcel, self)._from_address()
        schema["preAlert"].update({"allowed": [0, 11]})
        # strangely, civility seem really mandatory for shipper
        schema["civility"].update(
            {
                "required": True,
                "empty": False,
            }
        )
        return schema

    def _auth(self):
        schema = super(ChronopostFrApiParcel, self)._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"].update({"required": True, "empty": False, "maxlength": 6})
        schema["subAccount"] = {"type": "string", "maxlength": 3}
        return schema
