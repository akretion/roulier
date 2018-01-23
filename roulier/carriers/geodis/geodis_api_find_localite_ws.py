# -*- coding: utf-8 -*-
"""Implementation of Geodis Ws Api."""
from roulier.api import Api


class GeodisApiFindLocaliteWs(Api):

    def _service(self):
        schema = {}
        schema['is_test'] = {
            'type': 'boolean', 'default': True,
            'description': 'Use test Ws'}
        return schema

    def _address(self):
        schema = super(GeodisApiFindLocaliteWs, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        return {
            'country': schema['country'],
            'zip': schema['zip'],
            'city': schema['city'],
        }

    def _auth(self):
        schema = super(GeodisApiFindLocaliteWs, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['password']['required'] = False
        return schema

    def _schemas(self):
        return {
            'auth': self._auth(),
            'to_address': self._address(),
            'service': self._service(),
        }
