# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.api import Api, MyValidator
from .geodis_api_ws import GeodisApiWs


class GeodisApiEdi(Api):
    def _service(self):
        schema = {
            "depositId": {'type': 'string', 'default': ''},
            "depositDate": {'type': 'datetime', 'default': ''},
            "customerId": {'type': 'string', 'default': ''},
            "interchangeSender": {'type': 'string', 'default': ''},
            "interchangeRecipient": {'type': 'string', 'default': ''},
        }
        return schema

    def _address(self):
        schema = super(GeodisApiEdi, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        return schema

    def _from_address(self):
        schema = super(GeodisApiEdi, self)._from_address()
        schema['phone'].update({'required': True, 'empty': False})
        schema['street1']['required'] = True
        schema['siret'] = {
            'type': 'string', 'required': True,
            'default': '1234', 'empty': False}
        return schema

    def _parcel(self):
        ws_api = GeodisApiWs()
        return {
            'weight': ws_api._parcel()['weight'],
            'barcode': {
                'type': 'string', 'empty': False, 'default': '',
                'description': 'Barcode of the parcel'}
        }

    def _shipments(self):
        ws_api = GeodisApiWs()
        v = MyValidator()
        schema = {
            'to_address': {
                'type': 'dict',
                'schema': ws_api._to_address(),
                'default': v.normalized({}, ws_api._to_address())
            },
            'parcels': {
                'type': 'list',
                'schema': self._parcel(),
                'default': [v.normalized({}, self._parcel())]
            },
            'product': {'type': 'string', 'default': '', 'empty': False, 'required': True},
            'productOption': {'type': 'string', 'default': '', 'empty': True, 'required': False},
            'productTOD': {'type': 'string', 'default': '', 'empty': True, 'required': False},
            'reference1': {'type': 'string', 'default': '', 'empty': True},
            'reference2': {'type': 'string', 'default': '', 'empty': True},
            'reference3': {'type': 'string', 'default': '', 'empty': True},
        }
        return {
            "type": "list",
            "schema": {'type': 'dict', 'schema': schema},
            "default": [v.normalized({}, schema)],
        }

    def _schemas(self):
        return {
            'service': self._service(),
            'shipments': self._shipments(),
            'agency_address': self._from_address(),
            'from_address': self._from_address(),
        }

