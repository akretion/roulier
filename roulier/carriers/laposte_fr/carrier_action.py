"""Implementation for Laposte."""
from ...carrier_action import CarrierGetLabel
from ...carrier_action import CarrierGetPackingSlip
from ...roulier import factory
from .encoder import LaposteFrEncoder
from .encoder import LaposteFrEncoderGetPackingSlip
from .decoder import LaposteFrDecoderGetLabel
from .decoder import LaposteFrDecoderGetPackingSlip
from .transport import LaposteFrTransport
from .api import LaposteFrApiPackingSlip
from .api import LaposteFrApiParcel


class LaposteFrGetabel(CarrierGetLabel):
    """Implementation for Laposte."""

    ws_url = "https://ws.colissimo.fr/sls-ws/SlsServiceWS/2.0?wsdl"
    encoder = LaposteFrEncoder
    decoder = LaposteFrDecoderGetLabel
    transport = LaposteFrTransport
    api = LaposteFrApiParcel
    manage_multi_label = False


class LaposteFrGetPackingSlip(CarrierGetPackingSlip):
    """Implementation for Laposte."""

    ws_url = "https://ws.colissimo.fr/sls-ws/SlsServiceWS"
    encoder = LaposteFrEncoderGetPackingSlip
    decoder = LaposteFrDecoderGetPackingSlip
    transport = LaposteFrTransport
    api = LaposteFrApiPackingSlip
    manage_multi_slip = False


factory.register_builder("laposte_fr", "get_label", LaposteFrGetabel)
factory.register_builder("laposte_fr", "get_packing_slip", LaposteFrGetPackingSlip)
