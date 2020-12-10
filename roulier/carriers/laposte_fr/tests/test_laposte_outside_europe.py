# -*- coding: utf-8 -*-
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
    vals["customs"] = {
        "articles": [
            {
                "quantity": "2",
                "weight": 0.5,
                "originCountry": "FR",
                "description": "Printed circuits",
                "hs": "853400",
                "value": 1.0,
            }
        ],
        "category": 3,
    }
    vals["parcels"][0]["totalAmount"] = 123  # Frais de transport
    result = roulier.get("laposte_fr", "get_label", vals)
    label = assert_label(result)
    assert "data" in label
