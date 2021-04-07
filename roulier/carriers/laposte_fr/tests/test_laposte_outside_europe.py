import logging
import copy

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA
from .test_laposte_basic import _do_not_execute_test_on_remote
from .test_laposte_basic import assert_label


logger = logging.getLogger(__name__)


# TODO : UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe2 in position 7143: invalid continuation byte
def test_COM_product():
    """Outre-Mer - Colissimo Domicile - sans signature"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "COM"
    vals["service"]["transportationAmount"] = 123
    vals["service"]["totalAmount"] = 123
    vals["to_address"]["country"] = "GP"  # Guadeloupe
    vals["to_address"]["zip"] = "97100"  # Basse-Terre
    vals["parcels"][0]["customs"] = {
        "articles": [
            {
                "quantity": "2",
                "weight": 0.5,
                "originCountry": "FR",
                "description": "Printed circuits",
                "hsCode": "853400",
                "value": 1.0,
            }
        ],
        "category": 3,
    }
    vals["parcels"][0]["totalAmount"] = 123  # Frais de transport
    result = roulier.get("laposte_fr", "get_label", vals)
    label = assert_label(result)
    assert "data" in label


def test_full_customs_declarations():
    """Complete customsDeclarations"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "COM"
    vals["to_address"]["country"] = "GP"  # Guadeloupe
    vals["to_address"]["zip"] = "97100"  # Basse-Terre
    vals["parcels"][0]["customs"] = {
        "articles": [
            {
                "description": "Printed circuits",
                "quantity": "2",
                "weight": 0.5,
                "value": 1.0,
                "hsCode": "853400",
                "originCountry": "FR",
                "currency": "EUR",
                "artref": "artref",
                "originalIdent": "A",
                "vatAmount": 0,
                "customsFees": 0,
            }
        ],
        "category": 3,
        "original": {
            "originalIdent": "A",
            "originalInvoiceNumber": "111141111",
            "originalInvoiceDate": "2016-11-02",
            "originalParcelNumber": "7Q06270508932",
        },
        "importersReference": "",
        "importersContact": "",
        "officeOrigin": "",
        "comments": "comments",
        "description": "Fake description",
        "invoiceNumber": "111141111",
        "licenceNumber": "",
        "certificatNumber": "",
        "importerAddress": {
            "company": "company name",
            "lastName": "Lastname",
            "firstName": "Firstname",
            "line0": "line0",
            "line1": "line1",
            "line2": "line2",
            "line3": "line3",
            "country": "FR",
            "city": "city",
            "zip": "75007",
            "phone": "+12089145766",
            "mobile": "0600000007",
            "door1": "",
            "door2": "",
            "email": "email@email.fr",
            "intercom": "intercom",
            "language": "FR",
        },
    }
    vals["parcels"][0]["totalAmount"] = 123  # Frais de transport
    result = roulier.get("laposte_fr", "get_label", vals)
    label = assert_label(result)
    assert "data" in label
