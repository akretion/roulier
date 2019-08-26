# -*- coding: utf-8 -*-
"""Geodis XML -> Python."""
from roulier.codec import Decoder


class GeodisDecoderRestWs(Decoder):
    """Geodis XML -> Python."""

    def decode(self, payload, action):
        """Geodis JSON -> Python.
        payload[body] : dict
        payload[request] : Requests obj
        """
        body = payload['body']
        if action == 'trackingList':
            mapping = GeodisTrackingListApi()
            formatted = [
                mapping.extract(line) for
                line in body]
        else:
            # NOT implemented
            formatted = body
        return formatted


class GeodisTrackingListApi():

    def to_address(self):
        return {
            'street1': 'adresse1Dest',
            'street2': 'adresse2Dest',
            'country': 'codePaysDest',
            'zip': 'codePostalDest',
            'country_name': 'libellePaysDest',
            'name': 'nomDest',
            'city': 'villeDest',
        }

    def from_address(self):
        return {
            'street1': 'adresse1Exp',
            'street2': 'adresse2Exp',
            'country': 'codePaysExp',
            'zip': 'codePostalExp',
            'country_name': 'libellePaysExp',
            'name': 'nomExp',
            'city': 'villeExp',
        }

    def parcels(self):
        return {
            'weight': 'poids',
        }

    def service(self):
        return {
            "product": 'codeProduit',
            "agencyId": 'codeSa',
            "customerId": 'codeClient',
            "shippingId": 'noRecepisse',
            'shippingDate': 'dateDepart',
            'reference1': 'reference1',
            'reference2': 'reference2',
            'reference3': 'refDest',
            'option': 'codeOption',
        }

    def tracking(self):
        return {
            'statusDate': 'dateEtat',
            'estDeliveryDate': 'dateLivraison',
            'status': 'status',
            'statusDetails': 'libelleLongEtat',
            'trackingCode': 'noSuivi',
            'publicUrl': 'urlSuiviDestinataire',
            'proofUrl': 'urlImageEnlevementLivraison',
        }

    def schema(self):
        return {
            'parcels': self.parcels(),
            'service': self.service(),
            'from_address': self.from_address(),
            'to_address': self.to_address(),
            'tracking': self.tracking(),
        }

    def extract(self, data):
        schema = self.schema()
        self.add_tracking_code(data)
        return self.visit(data, schema)

    def visit(self, data, schema):
        out = {}
        for (key, val) in schema.items():
            if isinstance(val, dict):
                out[key] = self.visit(data, val)
            else:
                out[key] = data[val]
        return out

    def add_tracking_code(self, data):
        # MVL: mise en livraison
        # AAR: en cours acheminement
        # None: en attente prise en charge
        # LIV: livré
        # CFM: conforme
        if data['codeSituation'] == 'LIV':
            state = 'DELIVERED'
        elif data['codeSituation'] == 'SOL':
            state = 'RETURNED'
        elif data['codeSituation'] in ('MLV', 'AAR'):
            state = 'TRANSIT'
        else:
            state = 'UNKNOWN'
        data['status'] = state

# CODES=
# 'UNKNOWN',
# 'DELIVERED',
# 'TRANSIT',
# 'FAILURE',
# 'RETURNED'
