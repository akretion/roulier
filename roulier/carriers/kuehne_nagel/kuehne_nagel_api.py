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
            'serviceSystem': {'default': 3},
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
