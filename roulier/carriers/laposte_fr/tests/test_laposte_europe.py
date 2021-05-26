import logging
import copy
import pytest

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA
from .test_laposte_basic import _do_not_execute_test_on_remote
from .test_laposte_basic import assert_label

logger = logging.getLogger(__name__)


"""
Here is the format of laposte response:

{
    "parcels": [
        {
            "id": 1,
            "reference": "9V31904388888",
            "tracking": {
                "number": "9V31904388888",
                "url": "",
                "partner": "0069100119V3198888888802250T",
            },
            "label": {
                "data": b"EENUfn5DRCx+Q0NefkNUfg0KX...lhBDQpeUFc3OTkNCEsWV5YWg0K",
                "name": "label_1",
                "type": "ZPL_10x15_203dpi",
            },
        }
    ],
    "annexes": [],
}
"""


def test_DOM_product():
    """France - Colissimo Domicile - sans signature"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOM"
    result = roulier.get("laposte_fr", "get_label", vals)
    label = assert_label(result)
    assert "data" in label


def test_DOS_product():
    """France - Colissimo Domicile - avec signature"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOS"
    result = roulier.get("laposte_fr", "get_label", vals)
    label = assert_label(result)
    assert "data" in label


def test_DOM_product_raise():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOM"
    vals["to_address"]["zip"] = "99999"
    with pytest.raises(
        CarrierError,
        match="Le code pays ou le code postal du destinataire est incorrect "
        "pour le code produit fourni",
    ):
        roulier.get("laposte_fr", "get_label", vals)

    # 30108 = Le code postal de l'expéditeur ne correspond pas au pays
    vals["to_address"]["zip"] = "21000"
    vals["from_address"]["zip"] = "9999"
    with pytest.raises(CarrierError, match="30108"):
        roulier.get("laposte_fr", "get_label", vals)
