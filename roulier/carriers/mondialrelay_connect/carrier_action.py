"""Mondial Relay Connect API implementation (get_label)."""

from roulier.carrier_action import CarrierGetLabel
from roulier.roulier import factory

from .api import MondialRelayConnectApi
from .decoder import MondialRelayConnectDecoder
from .encoder import MondialRelayConnectEncoder
from .transport import MondialRelayConnectTransport


class MondialRelayConnectGetLabel(CarrierGetLabel):
    """Create a shipment and its label through the Mondial Relay Connect REST API."""

    ws_url = "https://connect-api.mondialrelay.com/api/shipment"
    ws_test_url = "https://connect-api-sandbox.mondialrelay.com/api/shipment"
    encoder = MondialRelayConnectEncoder
    decoder = MondialRelayConnectDecoder
    transport = MondialRelayConnectTransport
    api = MondialRelayConnectApi
    # One call carries the whole shipment (ParcelCount drives the labels).
    manage_multi_label = True


factory.register_builder(
    "mondialrelay_connect", "get_label", MondialRelayConnectGetLabel
)
