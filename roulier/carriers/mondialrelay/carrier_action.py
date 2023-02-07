"""Implementation for MondialRelay."""
from ...carrier_action import CarrierGetLabel, CarrierBase
from ...roulier import factory
from .encoder import (
    MondialRelayEncoderFindPickupSite,
    MondialRelayEncoderGetLabel,
)
from .decoder import (
    MondialRelayDecoderFindPickupSite,
    MondialRelayDecoderGetLabel,
)
from .transport import MondialRelayTransport
from .api import MondialRelayApiParcel, MondialRelayApiFindPickUpSite


class MondialRelayGetLabel(CarrierGetLabel):
    """Implementation for MondialRelay."""

    ws_url = "https://api.mondialrelay.com/Web_Services.asmx"
    encoder = MondialRelayEncoderGetLabel
    decoder = MondialRelayDecoderGetLabel
    transport = MondialRelayTransport
    api = MondialRelayApiParcel
    manage_multi_label = False


class MondialRelayFindPickUpSite(CarrierBase):
    """Implementation for MondialRelay."""

    is_test = False
    roulier_input = None

    ws_url = "https://api.mondialrelay.com/Web_Services.asmx"
    encoder = MondialRelayEncoderFindPickupSite
    decoder = MondialRelayDecoderFindPickupSite
    transport = MondialRelayTransport
    api = MondialRelayApiFindPickUpSite

    def find_pickup_site(self, carrier_type, action, data):
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)
        self.roulier_input = data

        payload = encoder.encode(data)
        response = transport.send(payload)
        decoder.decode(response, payload)
        return decoder.result


factory.register_builder("mondialrelay", "get_label", MondialRelayGetLabel)
factory.register_builder("mondialrelay", "find_pickup_site", MondialRelayFindPickUpSite)
