"""Abstract classes for different Carrier actions"""
from abc import ABC, abstractmethod


class Carrier(ABC):
    def __init__(self, carrier_type, action, **kwargs):
        self.carrier_type = carrier_type
        self.action = action

    @property
    @abstractmethod
    def ws_url(self):
        pass

    @property
    @abstractmethod
    def transport(self):
        pass

    @property
    @abstractmethod
    def encoder(self):
        pass

    @property
    @abstractmethod
    def decoder(self):
        pass

    @property
    @abstractmethod
    def api(self):
        pass

    ws_test_url = ""


class CarrierGetLabel(Carrier, ABC):

    is_test = False
    roulier_input = None

    @property
    @abstractmethod
    def manage_multi_label(self):
        """
        True if carrier webservice accept multiple parcels in one call or False
        if we have to make one call per parcels, even if it belongs to a same shipment
        """
        pass

    def get_label(self, carrier_type, action, data):
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)
        self.roulier_input = data

        parcels = data.get("parcels", []).copy()
        # one call to carrier webservice is enough
        if self.manage_multi_label or len(parcels) == 1:
            payload = encoder.encode(data)
            response = transport.send(payload)
            decoder.decode(response, payload)
        # one call by parcel
        else:
            for parcel in parcels:
                data["parcels"] = [parcel]
                payload = encoder.encode(data)
                response = transport.send(payload)
                decoder.decode(response, payload)
        return decoder.result
