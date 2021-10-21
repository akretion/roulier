# -*- coding: utf-8 -*-
"""Implementation of UPS Api."""
from roulier.api import Api


NOTIFICATION_CODES = ["2", "5", "6", "7", "8", "012", "013"]


class UpsApi(Api):

    def _auth(self):
        schema = super(UpsApi, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['isTest'] = {'type': 'boolean', 'default': False}
        schema['transaction_source'] = {'required': True, 'default': False, "empty": False}
        schema['license_number'] = {'required': True, 'default': False, "empty": False}
        schema['shipper_number'] = {'required': True, 'default': False, "empty": False}
        return schema

    def _address(self):
        schema = super(UpsApi, self)._address()
        schema.update({"vat": {"default": ""}})
        return schema

    def _service(self):
        schema = super(UpsApi, self)._service()
        schema["labelFormat"]["allowed"] = ["EPL", "PNG", "SPL", "ZPL", "GIF"]
        schema["labelFormat"]["default"] = "GIF"
        schema["notifications"] = {
            'type': 'list',
            'schema': {'schema': self._notification(), 'type': 'dict'}
        }
        return schema

    def _notification(self):
        return {
            "code": {
                "type": "string",
                "allowed": NOTIFICATION_CODES,
            },
            "email_to": {
                "type": "string",
            },
            "undeliverable_email": {
                "type": "string",
            },
        }

    def _parcels(self):
        """Allow multiple parcels."""
        schema = super(UpsApi, self)._parcels()
        del schema['items']
        schema['schema'] = self._parcel()
        return schema

    def _parcel(self):
        schema = super(UpsApi, self)._parcel()
        schema['reference'] = {
            'type': 'string', 'required': False,
            'empty': True, 'default': '',
            }
        schema['number_of_pieces'] = {
            'type': 'integer', 'required': False,
            'empty': True, 'default': '',
            }
        schema['packaging_code'] = {
            'type': 'string', 'required': True,
            'empty': False, 'default': '',
            }
        schema['weight_unit'] = {
            'type': 'string', 'required': False,
            'empty': False, 'default': 'KGS',
            }
        return schema
