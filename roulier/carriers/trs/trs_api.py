# -*- coding: utf-8 -*-
"""Implementation of TRS Api."""
from roulier.api import Api

TRS_LABEL_FORMAT = (
    'ZPL',
)


class TrsApi(Api):
    def _service(self):
        schema = super(TrsApi, self)._service()
        schema['labelFormat']['allowed'] = TRS_LABEL_FORMAT
        schema['labelFormat']['default'] = TRS_LABEL_FORMAT[0]
        schema['shippingId'].update({'required': True, 'empty': False})

        return schema

    def _address(self):
        schema = super(TrsApi, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        return schema

    def _from_address(self):
        schema = super(TrsApi, self)._from_address()
        schema['company'].update({'required': True, 'empty': False})
        schema['phone'].update({'required': False, 'empty': True})
        schema['street1']['required'] = False
        return schema

    def _auth(self):
        schema = super(TrsApi, self)._auth()
        schema['login'].update({'required': False, 'empty': True})
        schema['password']['required'] = False
        return schema

    def _schemas(self):
        # Santize all fields for zpl
        schemas = super(TrsApi, self)._schemas()
        for schema in schemas:
            for field in schemas[schema]:
                schemas[schema][field].update({'coerce': 'zpl'})
        return schemas
