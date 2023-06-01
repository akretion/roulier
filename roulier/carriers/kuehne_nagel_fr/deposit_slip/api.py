"""Implementation of Kuehne Nagel Api."""
from roulier.api import MyValidator
from ..get_label.api import KuehneNagelFrParcelApi


class KuehneNagelDepositApi(KuehneNagelFrParcelApi):
    def _contact_info(self):
        return {
            "name": {"type": "string", "default": "", "required": True, "empty": False},
            "siret": {"required": True, "empty": False},
            "number": {"required": True, "empty": False},
        }

    def _service_edi(self):
        schema = {
            "date": {"required": True, "empty": False},
            "hour": {"required": True, "empty": False},
            "depositNumber": {"required": True, "empty": False},
            "deliveryContract": {"default": "", "type": "string"},
            "shippingConfig": {"default": "P"},
            "vatConfig": {"default": "V"},
            "invoicingContract": {"required": True, "empty": False},
            "serviceSystem": {"default": "3"},
            "goodsName": {"default": ""},
        }
        return schema

    def _shipments(self):
        v = MyValidator()
        schema = {
            "to_address": {
                "type": "dict",
                "schema": self._to_address(),
                "default": v.normalized({}, self._to_address()),
            },
            "service": {
                "type": "dict",
                "schema": self._service(),
                "default": v.normalized({}, self._to_address()),
            },
            "parcels": {
                "type": "list",
                "schema": {"schema": self._parcel(), "type": "dict"},
                "default": [v.normalized({}, self._parcel())],
            },
        }
        return {
            "type": "list",
            "schema": {"type": "dict", "schema": schema},
            "default": [v.normalized({}, schema)],
        }

    def _schemas(self):
        return {
            "service": self._service_edi(),
            "shipments": self._shipments(),
            "auth": self._auth(),
            "sender_info": self._contact_info(),
            "recipient_info": self._contact_info(),
        }
