# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.api import Api

GEODIS_LABEL_FORMAT = (
    'PDF',
    'HTML',
    'EPL',
    'ZPL',
    'XML',
)


class GeodisApi(Api):
    def _service(self):
        schema = super(GeodisApi, self)._service()
        schema['labelFormat']['allowed'] = GEODIS_LABEL_FORMAT
        schema['labelFormat']['default'] = 'ZPL'
        schema['labelFormat'].update({'required': True, 'empty': False})
        schema['product'].update({'required': True, 'empty': False})
        schema['agencyId'].update({'required': True, 'empty': False})
        schema['customerId'].update({'required': True, 'empty': False})
        schema['shippingId'].update({'required': True, 'empty': False})
        schema['is_test'] = {
            'type': 'boolean', 'default': True,
            'description': 'Use test WS'}

        return schema

    def _address(self):
        schema = super(GeodisApi, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        return schema

    def _from_address(self):
        schema = super(GeodisApi, self)._from_address()
        schema['phone'].update({'required': True, 'empty': False})
        schema['street1']['required'] = False
        return schema

    def _auth(self):
        schema = super(GeodisApi, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['password']['required'] = False
        return schema
