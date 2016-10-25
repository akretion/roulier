# -*- coding: utf-8 -*-
"""Implementation of Kuehne Nagel Api."""
from roulier.api import Api


class KuehneNagelApi(Api):

    def _service(self):
        schema = super(KuehneNagelApi, self)._service()
        schema.update({
            'goodsName': {'default': ''},
            'epalQuantity': {'default': 0},
            'shippingOffice': {'required': True, 'empty': False},
            'shippingRound': {'required': True, 'empty': False},
            'shippingName': {'required': True, 'empty': False},
            'mhuQuantity': {'default': 1},
            'weight': {'default': 0},
            'volume': {'default': 0},
            'deliveryContract': {'default': ''},
            'exportHub': {'default': ''},
            'orderName': {'default': ''},
            'shippingConfig': {'default': 'P'},
            'vatConfig': {'default': 'V'},
            'invoicingContract': {'required': True, 'empty': False},
            'deliveryType': {'default': 'D'},
            'serviceSystem': {'default': '3'},
            'note': {'default': ''},
            'kuehneOfficeName': {'required': True, 'empty': False},
        })
        return schema

    def _parcel(self):
        schema = super(KuehneNagelApi, self)._parcel()
        schema.update({
            'barcode': {'default': ''},
            'number': {'default': 1},
        })
        return schema


class KuehneNagelDepositApi(Api):

    def _to_address(self):
        address = self._address()
        address['street1']['required'] = False
        address['country']['required'] = False
        address['city']['required'] = False
        address['zip']['required'] = False
        address.update({
            'siret': {'required': True, 'empty': False},
            'number': {'required': True, 'empty': False},
        })
        return address

    def _from_address(self):
        address = self._address()
        address.update({
            'siret': {'required': True, 'empty': False},
            'number': {'required': True, 'empty': False},
        })
        return address

    def _service(self):
        schema = super(KuehneNagelDepositApi, self)._service()
        schema.update({
            'date': {'required': True, 'empty': False},
            'hour': {'required': True, 'empty': False},
            'depositNumber': {'required': True, 'empty': False},
            'deliveryContract': {'default': ''},
            'shippingConfig': {'default': 'P'},
            'vatConfig': {'default': 'V'},
            'invoicingContract': {'required': True, 'empty': False},
            'serviceSystem': {'default': '3'},
            'goodsName': {'default': ''},
            'lineNumber': {'required': True, 'empty': False},
            'lines': {'type': 'list', 'default': []}
        })
        schema['shippingDate'] = {'required': False, 'empty': True}
        return schema

    def _parcel(self):
        schema = super(KuehneNagelDepositApi, self)._parcel()
        schema['weight'] = {'default': 0}
        return schema
