# -*- coding: utf-8 -*-
"""Implementation of Dummy Api."""
from roulier.api import Api

DUMMY_LABEL_FORMAT = (
    'ZPL',
)


class DummyApi(Api):
    def _service(self):
        schema = super(DummyApi, self)._service()
        schema['labelFormat']['allowed'] = DUMMY_LABEL_FORMAT
        schema['labelFormat']['default'] = 'ZPL'
        return schema

    def _to_address(self):
        schema = super(DummyApi, self)._to_address()
        schema['dept'] = {'default': '', 'description': 'Region code'}
        return schema

    def _parcel(self):
        schema = super(DummyApi, self)._parcel()
        schema['reference'] = {'default': '', 'description': 'Parcel reference'}
        return schema

    def _auth(self):
        schema = super(DummyApi, self)._auth()
        schema['login'].update({'required': False})
        schema['password'].update({'required': False})
        return schema
