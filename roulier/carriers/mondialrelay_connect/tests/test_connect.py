"""Offline tests for the Mondial Relay Connect carrier."""

import copy

import pytest
from lxml import etree

from roulier import roulier
from roulier.roulier import factory
from roulier.exception import CarrierError, InvalidApiInput

from .data import DATA, RESPONSE_ERROR, RESPONSE_OK


def _text(root, tag):
    nodes = root.xpath("//*[local-name()=$t]", t=tag)
    return nodes[0].text if nodes else None


def _node(root, tag):
    nodes = root.xpath("//*[local-name()=$t]", t=tag)
    return nodes[0] if nodes else None


def test_carrier_registered():
    available = roulier.get_carriers_action_available()
    assert "mondialrelay_connect" in available
    assert available["mondialrelay_connect"] == ["get_label"]


def test_invalid_input_missing_recipient_zip():
    vals = copy.deepcopy(DATA)
    del vals["to_address"]["zip"]
    with pytest.raises(InvalidApiInput):
        carrier = factory.get("mondialrelay_connect", "get_label")
        carrier.encoder(carrier).encode(vals)


def test_invalid_delivery_mode():
    vals = copy.deepcopy(DATA)
    vals["service"]["deliveryMode"] = "NOPE"
    with pytest.raises(InvalidApiInput):
        carrier = factory.get("mondialrelay_connect", "get_label")
        carrier.encoder(carrier).encode(vals)


def test_encode_request_structure():
    carrier = factory.get("mondialrelay_connect", "get_label")
    payload = carrier.encoder(carrier).encode(copy.deepcopy(DATA))
    root = etree.fromstring(payload["body"])

    # Context.
    assert _text(root, "Login") == "BDTEST"
    assert _text(root, "CustomerId") == "BDTEST"
    assert _text(root, "Culture") == "fr-FR"
    assert _text(root, "VersionAPI") == "1.0"

    # Output options.
    assert _text(root, "OutputType") == "ZplCode"
    assert _text(root, "OutputFormat") == "Generic_ZPL_10x15_203dpi"

    # Shipment routing + free data.
    assert _text(root, "OrderNo") == "CMD123"
    assert _text(root, "CustomerNo") == "CLI1"
    assert _text(root, "ParcelCount") == "1"
    delivery = _node(root, "DeliveryMode")
    assert delivery.get("Mode") == "24R"
    assert delivery.get("Location") == "FR-66974"

    # Weight in grams, dimensions in cm.
    weight = _node(root, "Weight")
    assert weight.get("Value") == "1200"
    assert weight.get("Unit") == "gr"
    assert _node(root, "Length").get("Value") == "30"

    # Recipient mapping + delivery instruction.
    assert _text(root, "DeliveryInstruction") == "Etage 3, digicode 1234"
    recipient = root.xpath("//*[local-name()='Recipient']")[0]
    add1 = recipient.xpath(".//*[local-name()='AddressAdd1']")[0]
    add3 = recipient.xpath(".//*[local-name()='AddressAdd3']")[0]
    assert add1.text == "Jean Client"
    assert add3.text == "Batiment B"


def test_encode_weight_floor():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["weight"] = 0.001  # below the 10 g floor
    carrier = factory.get("mondialrelay_connect", "get_label")
    payload = carrier.encoder(carrier).encode(vals)
    root = etree.fromstring(payload["body"])
    assert _node(root, "Weight").get("Value") == "10"


def test_decode_success():
    carrier = factory.get("mondialrelay_connect", "get_label")
    carrier.roulier_input = copy.deepcopy(DATA)
    decoder = carrier.decoder(carrier)
    decoder.decode(
        {"body": RESPONSE_OK, "response": None}, {"output_type": "ZplCode"}
    )
    parcels = decoder.result["parcels"]
    assert len(parcels) == 1
    assert parcels[0]["tracking"]["number"] == "29A00012345"
    assert parcels[0]["reference"] == "PARCEL-1"
    assert parcels[0]["label"]["type"] == "ZplCode"
    assert "^XA" in parcels[0]["label"]["data"]


def test_decode_business_error():
    carrier = factory.get("mondialrelay_connect", "get_label")
    carrier.roulier_input = copy.deepcopy(DATA)
    decoder = carrier.decoder(carrier)
    with pytest.raises(CarrierError, match="Invalid postcode"):
        decoder.decode(
            {"body": RESPONSE_ERROR, "response": None}, {"output_type": "ZplCode"}
        )
