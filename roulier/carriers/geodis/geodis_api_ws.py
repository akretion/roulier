# -*- coding: utf-8 -*-
"""Implementation of Geodis Ws Api."""
from roulier.api import Api

GEODIS_LABEL_FORMAT = (
    'PDF',
    'HTML',
    'EPL',
    'ZPL',
    'XML',
)
GEODIS_ALLOWED_NOTIFICATIONS = (
    'M',  # Mail
    'S',  # SMS
    'P',  # Mail & SMS
)


class GeodisApiWs(Api):
    def _service(self):
        schema = super(GeodisApiWs, self)._service()
        schema['labelFormat']['allowed'] = GEODIS_LABEL_FORMAT
        schema['labelFormat']['default'] = 'ZPL'
        schema['labelFormat'].update({'required': True, 'empty': False})
        schema['product'].update({'required': True, 'empty': False})
        schema['agencyId'].update({'required': False, 'empty': True})
        schema['customerId'].update({'required': True, 'empty': False})
        schema['shippingId'].update({'required': True, 'empty': False})
        schema['hubId'] = {
            'description': 'TEOS : code agence Hub de sortie',
            'default': ''
        }
        schema['is_test'] = {
            'type': 'boolean', 'default': True,
            'description': 'Use test Ws'}
        schema['option'] = {
            'type': 'string', 'default': False,
            'description': """Options (RDW, RDV, ETG, ...)"""}
        schema['notification'] = {
            'default': GEODIS_ALLOWED_NOTIFICATIONS[0],
            'allowed': GEODIS_ALLOWED_NOTIFICATIONS}

        return schema

    def _address(self):
        schema = super(GeodisApiWs, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        return schema

    def _from_address(self):
        schema = super(GeodisApiWs, self)._from_address()
        schema['phone'].update({'required': True, 'empty': False})
        schema['street1']['required'] = False
        return schema

    def _auth(self):
        schema = super(GeodisApiWs, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['password']['required'] = False
        return schema

    def _parcel(self):
        schema = super(GeodisApiWs, self)._parcel()
        schema['volume'] = {
            'type': 'float', 'required': False,
            'empty': True, 'default': 0}
        schema['reference'] = {
            'type': 'string', 'required': False,
            'empty': True, 'default': '',
            'description': 'Description of this parcel'}
        return schema

    def _parcels(self):
        """Allow multiple parcels."""
        schema = super(GeodisApiWs, self)._parcels()
        del schema['items']
        schema['schema'] = self._parcel()
        return schema
