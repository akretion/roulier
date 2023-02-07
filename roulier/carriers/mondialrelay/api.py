"""Implementation of MondialRelay Api."""
from roulier.api import ApiParcel, BaseApi, MyValidator


class MRValidator(MyValidator):
    def _normalize_coerce_french_boolean(self, value):
        if value is None:
            return value
        return "O" if value else "N"


class MondialRelayApiParcel(ApiParcel):
    def _validator(self):
        v = MRValidator()
        v.allow_unknown = True
        # v.purge_unknown = True
        return v

    def _service(self):
        schema = super()._service()
        for field in [
            "agencyId",
            "shippingDate",
            "reference1",
            "reference2",
            "reference3",
        ]:
            del schema[field]

        schema["labelFormat"]["allowed"] = [
            "PDF",
            "JSON",
        ]
        schema["labelFormat"]["default"] = "PDF"
        return {
            **schema,
            "pickupMode": {
                "type": "string",
                "default": "",
                "required": True,
                "empty": False,
            },
            "cashOnDelivery": {
                "type": "integer",
                "default": 0,
                "required": True,
                "empty": False,
            },
            "cashOnDeliveryCurrency": {"type": "string", "default": "EUR"},
            "price": {"type": "integer", "default": None, "nullable": True},
            "currency": {"type": "string", "default": "EUR"},
            "pickupCountry": {"type": "string", "default": ""},
            "pickupSite": {"type": "string", "default": ""},
            "shippingCountry": {"type": "string", "default": ""},
            "shippingSite": {"type": "string", "default": ""},
            "notice": {
                "type": "boolean",
                "default": None,
                "nullable": True,
                "coerce": "french_boolean",
            },
            "takeBack": {
                "type": "boolean",
                "default": None,
                "coerce": "french_boolean",
                "nullable": True,
            },
            "assemblyTime": {"type": "integer", "default": None, "nullable": True},
            "insurance": {"type": "integer", "default": None, "nullable": True},
            "text": {"type": "string", "default": ""},
        }

    def _address(self):
        schema = super()._address()
        # Lang: for dest in (FR, ES, NL, EN), for exp any iso
        schema["lang"] = {
            "type": "string",
            "default": "",
            "required": True,
            "empty": False,
        }
        schema["country"].update({"required": True, "empty": False})
        schema["zip"].update({"required": True, "empty": False})
        schema["city"].update({"required": True, "empty": False})

        # Name -> ad1
        # Company -> ad2
        # Street1 -> ad3
        # Street2 -> ad4
        # phone -> tel1
        # phone2 -> tel2
        # email -> mail

        schema["street1"].update({"required": True, "empty": False})
        schema["phone2"] = {"type": "string", "default": ""}
        return schema

    def _from_address(self):
        address = self._address()
        address["phone"].update({"required": True, "empty": False})
        return address

    def _to_address(self):
        address = self._address()
        return address

    def _parcel(self):
        schema = super()._parcel()
        schema["length"] = {"type": "integer", "default": None, "nullable": True}
        schema["height"] = {"type": "string", "default": ""}
        schema["count"] = {
            "type": "integer",
            "default": 1,
            "required": True,
            "empty": False,
        }

        return schema

    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"].update({"required": True, "empty": False})
        return schema

    def _schemas(self):
        schemas = super()._schemas()
        return schemas


class MondialRelayApiFindPickUpSite(BaseApi):
    def _search(self):
        return {
            "country": {
                "type": "string",
                "default": "",
                "required": True,
                "empty": False,
            },
            "id": {"type": "integer", "default": None, "nullable": True},
            "zip": {
                "type": "string",
                "default": "",
            },
            "lat": {
                "type": "string",
                "default": "",
            },
            "lng": {
                "type": "string",
                "default": "",
            },
            "weight": {"type": "float", "default": None, "nullable": True},
            "action": {
                "type": "string",
                "default": "",
            },
            "delay": {"type": "integer", "default": 0},
            "searchRadius": {
                "type": "integer",
                "default": 10,
            },
            "actionType": {
                "type": "string",
                "default": "",
            },
            "resultsCount": {
                "type": "integer",
                "default": 20,
                "required": True,
                "empty": False,
            },
        }

    def _schemas(self):
        return {"auth": self._auth(), "search": self._search()}
