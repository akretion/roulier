# -*- coding: utf-8 -*-
"""Implementation of Dpd Api."""
from roulier.api import Api

DPD_LABEL_FORMAT = (
    'PDF',
    'PNG',
    'ZPL',
)

DPD_ALLOWED_NOTIFICATIONS = (
    'No',
    'Predict',
    'AutomaticSMS',
    'AutomaticMail',
)
DPD_PRODUCTS = (
    'DPD_Classic',
    'DPD_Relais',
    'DPD_Predict',
    # 'DPD Retour en Relais',  # Not implemented yet
)


class DpdApi(Api):
    def _service(self):
        schema = super(DpdApi, self)._service()
        schema['labelFormat']['allowed'] = DPD_LABEL_FORMAT
        schema['labelFormat']['default'] = 'ZPL'
        schema['labelFormat'].update({'required': True, 'empty': False})
        schema['agencyId'].update({
            'required': True, 'empty': False,
            'description': 'Agency code int(3)'})
        schema['customerCountry'] = {
            'required': True, 'empty': False,
            'description': 'Customer country code (France = 250) int(3)'}
        schema['customerId'].update({
            'required': True, 'empty': False,
            'description': 'Customer number int(6)'})
        schema['shippingDate'].update({'required': False, 'empty': True})

        # mettre ça ensemble ?
        schema['notifications'] = {
            'default': DPD_ALLOWED_NOTIFICATIONS[0],
            'allowed': DPD_ALLOWED_NOTIFICATIONS}
        schema['product'].update({
            'empty': False,
            'required': True,
            'default': DPD_PRODUCTS[0],
            'description': 'Type de produit',
            'allowed': DPD_PRODUCTS
        })

        schema['dropOffLocation'] = {
            'default': '',
            'empty': True,
            'required': False,
            'description': 'Drop-off Location id (Relais Colis)'
        }

        return schema

    def _address(self):
        schema = super(DpdApi, self)._address()
        schema['street2']['description'] = (
            "N/A for DPD. It will be appended to street1")
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        return schema

    def _to_address(self):
        schema = super(DpdApi, self)._to_address()
        schema['firstName'] = {'default': '', 'description': """First name""",
            'coerce': 'accents'}
        schema['door1'] = {'default': '', 'description': """Door code 1"""}
        schema['door2'] = {'default': '', 'description': """Door code 2"""}
        schema['intercom'] = {'default': '', 'description': """Intercom"""}
        for field in ['city', 'company', 'name', 'street1', 'street2']:
            schema[field].update({ 'coerce': 'accents'})
        return schema

    def _from_address(self):
        schema = super(DpdApi, self)._from_address()
        schema['phone'].update({'required': True, 'empty': False})
        return schema

    def _auth(self):
        schema = super(DpdApi, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['password']['required'] = False
        return schema
