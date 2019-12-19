# -*- coding: utf-8 -*-
"""Dpd XML -> Python."""
from roulier.codec import Decoder
from exceptions import NotImplementedError


class DpdDecoder(Decoder):
    """Dpd json response -> Python."""


    def decode(self, payload, request, action):
        """Dpd JSON -> Python.
        payload: response as dict
        request: requests
        """
        if action == 'createShipmentWithLabels':
            mapping = DpdApiGetLabelMappingOut()
            return mapping.normalize(payload, request)
        else:
            raise NotImplementedError(action)


class DpdApiGetLabelMappingOut():
    """Convert external schema to roulier responses
    internal: what goes to the user
    external: what comes from the remote endpoint
    out: external -> internal

    We try to stick to other carriers response to
    get_label()
    """

    def normalize(self, output_data, input_data):
        # input_data is the what was sent to WS
        # output_data is the payload returned by WS
        val = {
            "annexes": [],
        }
        val.update(self._tracking(output_data))
        val.update(self._main_label(output_data))
        val.update(self._parcels(output_data, input_data))
        return val

    def _parcels(self, data, input_data):
        ship = data['shipments'][0] # for the moment
        # we only support one shipment
        return {
            "parcels": [
                self._parcel(parcel, data, input_data)
                for parcel in ship['parcels']
            ]
        }
    
    def _parcel(self, parcel, data, input_data):
        ref = input_data['parcels'][0].get('cref1', '')
        label = data['label']
        return {
            "id": parcel,
            "number": parcel,
            "reference": ref,
            "label": self._label(label),
        }
    
    def _tracking(self, data):
        ship = data['shipments'][0]
        return {
            "tracking": { "number": ship['parcels'][0]}
        }

    def _label(self, data):
        return {
            "name": data['fileName'],
            "data": data['fileContent'],
            "type": data['fileType'],
        }
    def _main_label(self, data):
        return {
            "label": self._label(data['label'])
        }