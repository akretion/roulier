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


class CarrierGetLabel(Carrier, ABC):

    def get_label(self, carrier_type, action, data):
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)

        payload = encoder.encode(data)
        response = transport.send(payload)
        return decoder.decode(response, payload)
