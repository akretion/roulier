"""Implementation for Laposte."""
from ...carrier_action import CarrierGetLabel
from ...carrier_action import CarrierGetPackingSlip
from ...carrier_action import CarrierParcelDocument
from ...roulier import factory
from .encoder import LaposteFrEncoder
from .encoder import LaposteFrEncoderGetPackingSlip
from .encoder import LaposteFrEncoderParcelDocument
from .decoder import LaposteFrDecoderGetLabel
from .decoder import LaposteFrDecoderGetPackingSlip
from .decoder import LaposteFrDecoderParcelDocument
from .transport import LaposteFrTransport
from .transport import LaposteFrParcelDocumentTransport
from .api import LaposteFrApiPackingSlip
from .api import LaposteFrApiParcel
from .api import LaposteFrApiParcelDocument


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


class LaposteFrParcelDocument(CarrierParcelDocument):
    """Implementation for Laposte."""

    ws_url = "https://ws.colissimo.fr/api-document/rest/"
    encoder = LaposteFrEncoderParcelDocument
    decoder = LaposteFrDecoderParcelDocument
    transport = LaposteFrParcelDocumentTransport
    api = LaposteFrApiParcelDocument


factory.register_builder("laposte_fr", "get_label", LaposteFrGetabel)
factory.register_builder("laposte_fr", "get_packing_slip", LaposteFrGetPackingSlip)
factory.register_builder("laposte_fr", "get_documents", LaposteFrParcelDocument)
factory.register_builder("laposte_fr", "get_document", LaposteFrParcelDocument)
factory.register_builder("laposte_fr", "create_document", LaposteFrParcelDocument)
factory.register_builder("laposte_fr", "update_document", LaposteFrParcelDocument)
