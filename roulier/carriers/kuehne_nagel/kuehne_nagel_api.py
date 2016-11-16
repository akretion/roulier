# -*- coding: utf-8 -*-
"""Implementation of Kuehne Nagel Api."""
from roulier.api import Api


class KuehneNagelApi(Api):

    def _service(self):
        schema = super(KuehneNagelApi, self)._service()
        schema.update({
            'goodsName': {'default': ''},
            'epalQuantity': {'default': 0},
            'labelShippingDate': {'required': True, 'empty': False},
            'shippingOffice': {'required': True, 'empty': False},
            'shippingRound': {'required': True, 'empty': False},
            'shippingName': {'required': True, 'empty': False},
            'mhuQuantity': {'default': 1},
            'weight': {'default': 0},
            'volume': {'default': 0},
            'deliveryContract': {'default': '', 'type': 'string'},
            'labelDeliveryContract': {'default': 'C', 'type': 'string'},
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

    def _contact_info(self):
        return {
            'name': {'type': 'string', 'default': '', 'required': True, 'empty': False},
            'siret': {'required': True, 'empty': False},
            'number': {'required': True, 'empty': False},
        }

    def _service(self):
        schema = super(KuehneNagelDepositApi, self)._service()
        schema.update({
            'date': {'required': True, 'empty': False},
            'hour': {'required': True, 'empty': False},
            'depositNumber': {'required': True, 'empty': False},
            'deliveryContract': {'default': '', 'type': 'string'},
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

    def _schemas(self):
        return {
            'service': self._service(),
            'auth': self._auth(),
            'sender_info': self._contact_info(),
            'recipient_info': self._contact_info(),
        }

