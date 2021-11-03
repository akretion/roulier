"""Implementation for MondialRelay."""
from ...carrier_action import CarrierGetLabel, Carrier
from ...roulier import factory
from .encoder import (
    MondialRelayEncoderFindPickupSite,
    MondialRelayEncoderGetLabel,
    MondialRelayEncoderGetLabelUrl,
)
from .decoder import (
    MondialRelayDecoderFindPickupSite,
    MondialRelayDecoderGetLabel,
    MondialRelayDecoderGetLabelUrl,
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


class MondialRelayGetLabelUrl(CarrierGetLabel):
    """Implementation for MondialRelay."""

    ws_url = "https://api.mondialrelay.com/Web_Services.asmx"
    encoder = MondialRelayEncoderGetLabelUrl
    decoder = MondialRelayDecoderGetLabelUrl
    transport = MondialRelayTransport
    api = MondialRelayApiParcel
    manage_multi_label = False

    def get_label_url(self, carrier_type, action, data):
        return super().get_label(carrier_type, action, data)


class MondialRelayFindPickUpSite(Carrier):
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


factory.register_builder("mondial_relay", "get_label", MondialRelayGetLabel)
factory.register_builder("mondial_relay", "get_label_url", MondialRelayGetLabelUrl)
factory.register_builder(
    "mondial_relay", "find_pickup_site", MondialRelayFindPickUpSite
)
