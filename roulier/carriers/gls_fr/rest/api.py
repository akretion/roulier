"""Implementation of Laposte Api."""

from roulier.api import ApiParcel

from .constants import SERVICE_CHOICES
from .constants import SERVICE_STANDARD


class GlsEuApiParcel(ApiParcel):
    def _service(self):
        schema = super()._service()
        schema["language"] = {"default": "en"}
        schema["product"].update(
            {
                "type": "string",
                "default": SERVICE_STANDARD,
                "allowed": tuple(SERVICE_CHOICES),
            }
        )
        schema["pickupLocationId"] = {"type": "string"}
        schema["labelSize"] = {
            "type": "string",
            "default": "A6",
            "allowed": ["A6", "A5", "A4"],
        }
        schema["labelFormat"].update(
            {
                "type": "string",
                "default": "PDF",
                "allowed": ["PDF", "PNG", "ZPL"],
            }
        )
        schema["incoterm"] = {
            "type": "string",
            # "regex": r"^\d{2}$",
            # "allowed": ["10", "13", 18", "20", "23", "30", "40", "43", "50", "60"],
        }
        return schema

    def _address(self):
        string_1_10 = {"type": "string", "minlength": 1, "maxlength": 10}
        string_2_35 = {"type": "string", "minlength": 2, "maxlength": 35}
        string_0_35 = {"type": "string", "minlength": 0, "maxlength": 35}
        schema = super()._address()
        schema["name"].update(string_2_35)
        schema["street1"].update({"minlength": 3, "maxlength": 35})
        schema["country"].update({"minlength": 2, "maxlength": 2})
        schema["zip"].update(string_1_10)
        schema["phone"].update({"maxlength": 20})
        schema["email"].update(
            {
                "required": True,
                "minlength": 3,
                "maxlength": 100,
            }
        )
        schema["city"].update(string_2_35)
        schema.update(
            {
                "id": {"type": "string", "minlength": 0, "maxlength": 20},
                "street2": string_0_35,
                "street3": string_0_35,
                "blockNo1": string_1_10,
                "province": string_2_35,
                "contact": string_2_35,
                "mobile": schema["phone"],
            }
        )
        return schema

    def _opt_schema(self, schema):
        return {
            "type": "dict",
            "required": False,
            "schema": schema,
        }

    def _parcel(self):
        schema = super()._parcel()
        schema.update(
            {
                "services": {
                    "type": "list",
                    "schema": {
                        "schema": {
                            "product": {
                                "type": "string",
                                "allowed": tuple(SERVICE_CHOICES),
                            },
                            "pickupLocationId": {"type": "string"},
                        },
                        "type": "dict",
                    },
                },
                "reference2": {"type": "string"},
                "comment": {"type": "string", "maxlength": 35},
            }
        )
        return schema

    def _returns(self):
        return {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "weight": {
                        "type": "float",
                        "default": "",
                        "required": True,
                        "empty": False,
                    }
                },
            },
            "empty": False,
            "required": False,
        }

    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"].update({"required": True, "empty": False})
        return schema

    def _schemas(self):
        schema = super()._schemas()
        schema["returns"] = self._returns()
        schema["to_address"] = self._opt_schema(self._to_address())
        schema["from_address"] = self._opt_schema(self._address())
        schema["return_address"] = self._opt_schema(self._address())
        schema["pickup_address"] = self._opt_schema(self._address())
        return schema
