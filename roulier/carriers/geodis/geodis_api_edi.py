# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.api import Api, MyValidator
from .geodis_api_ws import GeodisApiWs, GEODIS_ALLOWED_NOTIFICATIONS


class GeodisApiEdi(Api):
    def _service(self):
        schema = {
            "depositId": {
                "type": "string",
                "coerce": "accents",
                "default": "",
                "empty": False,
                "required": True,
            },
            "depositDate": {
                "type": "datetime",
                "coerce": "accents",
                "default": "",
                "empty": False,
                "required": True,
            },
            "customerId": {
                "type": "string",
                "coerce": "accents",
                "default": "",
                "empty": False,
                "required": True,
            },
            "interchangeSender": {
                "type": "string",
                "coerce": "accents",
                "default": "",
                "empty": False,
                "required": True,
            },
            "interchangeRecipient": {
                "type": "string",
                "coerce": "accents",
                "default": "",
                "empty": False,
                "required": True,
            },
        }
        return schema

    def _address(self):
        schema = super(GeodisApiEdi, self)._address()
        schema["country"].update({"required": True, "empty": False, "maxlength": 2})
        schema["zip"].update({"required": True, "empty": False})
        schema["city"].update({"required": True, "empty": False})
        for key in schema:
            if schema[key].get("type", "") == "string":
                schema[key].update({"coerce": "accents"})
        return schema

    def _from_address(self):
        schema = super(GeodisApiEdi, self)._from_address()
        schema["phone"].update({"required": True, "empty": False})
        schema["street1"]["required"] = True
        schema["siret"] = {
            "type": "string",
            "required": True,
            "default": "",
            "empty": False,
        }
        for key in schema:
            if schema[key].get("type", "") == "string":
                schema[key].update({"coerce": "accents"})
        return schema

    def _parcel(self):
        weight = GeodisApiWs()._parcel()["weight"]
        return {
            "weight": weight,
            # 'description': 'Barcode of the parcel'
            "barcode": {
                "type": "string",
                "empty": False,
                "default": "",
                "required": True,
                "coerce": "accents",
            },
        }

    def _to_address(self):
        schema = GeodisApiWs()._to_address()
        for key in schema:
            if schema[key].get("type", "") == "string":
                schema[key].update({"coerce": "accents"})
        return schema

    def _shipments(self):
        v = MyValidator()
        schema = {
            "to_address": {
                "type": "dict",
                "schema": self._to_address(),
                "default": v.normalized({}, self._to_address()),
            },
            "parcels": {
                "type": "list",
                "schema": self._parcel(),
                "default": [v.normalized({}, self._parcel())],
            },
            "product": {
                "type": "string",
                "default": "",
                "empty": False,
                "required": True,
            },
            "productTOD": {
                "type": "string",
                "default": "",
                "empty": True,
                "required": False,
            },
            "productPriority": {
                "type": "string",
                "default": "",
                "empty": True,
                "required": False,
                # 'description': """4219, 1: express, 3: normal speed"""
            },
            "productOption": {
                "type": "string",
                "default": "",
                "empty": True,
                "required": False,
                # 'description': """7273, like RDV, B2C, BRT, AEX, A2P..."""
            },
            "notifications": {
                "type": "string",
                "default": GEODIS_ALLOWED_NOTIFICATIONS[0],
                "allowed": GEODIS_ALLOWED_NOTIFICATIONS,
                "required": False,
                # 'description': """7085 : Notify recipient by M(ail), S(ms), P(=M+S)"""
            },
            "shippingId": {
                "type": "string",
                "default": "",
                "empty": False,
                "required": True,
            },
            "reference1": {"type": "string", "default": "", "empty": True},
            "reference2": {"type": "string", "default": "", "empty": True},
            "reference3": {"type": "string", "default": "", "empty": True},
        }
        return {
            "type": "list",
            "schema": {"type": "dict", "schema": schema},
            "default": [v.normalized({}, schema)],
        }

    def _schemas(self):
        schemas = {
            "service": self._service(),
            "shipments": self._shipments(),
            "agency_address": self._from_address(),
            "from_address": self._from_address(),
        }
        return schemas
