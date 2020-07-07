# -*- coding: utf-8 -*-
import logging
import copy
import base64
import requests
import shutil
import pytest

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA

logger = logging.getLogger(__name__)

DOWNLOAD_PDF_FILE = False  # Update to get demo files

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


def test_methods():
    assert "laposte_fr" in roulier.get_carriers_action_available().keys()
    assert roulier.get_carriers_action_available()["laposte_fr"] == ["get_label"]


def test_auth():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["auth"]["login"] = "test"
    vals["service"]["product"] = "COL"
    with pytest.raises(CarrierError, match="Identifiant ou mot de passe incorrect"):
        roulier.get("laposte_fr", "get_label", vals)

    vals = copy.deepcopy(DATA)
    vals["auth"]["password"] = "test"
    vals["service"]["product"] = "COL"
    with pytest.raises(CarrierError, match="Identifiant ou mot de passe incorrect"):
        roulier.get("laposte_fr", "get_label", vals)


def test_DOM_product():
    """France - Colissimo Domicile - sans signature"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOM"
    result = roulier.get("laposte_fr", "get_label", vals)
    parcel = result["parcels"][0]
    assert sorted(parcel.keys()) == ["id", "label", "reference", "tracking"], True

    vals["to_address"]["zip"] = "99999"
    with pytest.raises(
        CarrierError,
        match="Le code pays ou le code postal du destinataire est incorrect pour le code produit fourni",
    ):
        roulier.get("laposte_fr", "get_label", vals)

    # 30108 = Le code postal de l'expéditeur ne correspond pas au pays
    vals["to_address"]["zip"] = "21000"
    vals["from_address"]["zip"] = "9999"
    with pytest.raises(CarrierError, match="30108"):
        roulier.get("laposte_fr", "get_label", vals)


def test_DOS_product():
    """France - Colissimo Domicile - avec signature"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOS"
    result = roulier.get("laposte_fr", "get_label", vals)
    parcel = result["parcels"][0]
    assert sorted(parcel.keys()) == ["id", "label", "reference", "tracking"], True


def test_CORE_product():
    """France - Colissimo Retour France"""
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "CORE"
    vals["to_address"]["company"] = "InfoSaône"
    result = roulier.get("laposte_fr", "get_label", vals)
    parcel = result["parcels"][0]
    assert sorted(parcel.keys()) == ["id", "label", "reference", "tracking"], True


# TODO : UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe2 in position 7143: invalid continuation byte
# def test_COM_product():
#    """Outre-Mer - Colissimo Domicile - sans signature"""
#    if _do_not_execute_test_on_remote():
#        return
#    vals = copy.deepcopy(DATA)
#    vals["service"]["product"] = "COM"
#    vals["service"]["transportationAmount"] = 123
#    vals["service"]["totalAmount"] = 123
#    vals["to_address"]["country"] = "GP" # Guadeloupe
#    vals["to_address"]["zip"] = "97100"  # Basse-Terre
#    vals["customs"]={
#        "articles":[
#            {
#                "quantity":"2",
#                "weight":0.5,
#                "originCountry":"FR",
#                "description":"Printed circuits",
#                "hs":"853400",
#                "value":1.0
#            }
#        ],
#        "category":3
#    }
#    vals["parcels"][0]["totalAmount"] = 123 # Frais de transport
#    result = roulier.get("laposte_fr", "get_label", vals)
#    parcel = result["parcels"][0]
#    assert (sorted(parcel.keys())==["id", "label", "reference", "tracking"]), True


# TODO idem ci-dessus
# def test_CDS_product():
#    """Outre-Mer - Colissimo Domicile - avec signature"""
#    if _do_not_execute_test_on_remote():
#        return
#    vals = copy.deepcopy(DATA)
#    vals["service"]["product"] = "CDS"
#    roulier.get("laposte_fr", "get_label", vals)


# TODO idem ci-dessus
# def test_CORI_product():
#    """Outre-Mer - Colissimo Retour OM"""
#    if _do_not_execute_test_on_remote():
#        return
#    vals = copy.deepcopy(DATA)
#    vals["service"]["product"] = "CORI"
#    roulier.get("laposte_fr", "get_label", vals)


# TODO : Le type de choix retour n'a pas été transmis
# def test_COLI_product():
#    """International - Colissimo Expert International"""
#    if _do_not_execute_test_on_remote():
#        return
#    vals = copy.deepcopy(DATA)
#    vals["service"]["product"] = "COLI"
#    vals["service"]["totalAmount"] = 123
#    vals["to_address"]["country"] = "TN" # Tunisie
#    vals["to_address"]["zip"] = "1000"   # Tunis
#    vals["customs"]={
#        "articles":[
#            {
#                "quantity":"2",
#                "weight":0.5,
#                "originCountry":"FR",
#                "description":"Printed circuits",
#                "hs":"853400",
#                "value":1.0
#            }
#        ],
#        "category":3
#    }
#    result = roulier.get("laposte_fr", "get_label", vals)
#    parcel = result["parcels"][0]
#    assert (sorted(parcel.keys())==["id", "label", "reference", "tracking"]), True


def test_label_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        roulier.get("laposte_fr", "get_label", DATA)
    vals = copy.deepcopy(DATA)

    vals["service"]["product"] = "whatisitproduct"
    with pytest.raises(CarrierError, match="Le code produit est incorrect"):
        roulier.get("laposte_fr", "get_label", vals)

    vals["service"]["product"] = "COL"
    vals["parcels"][0]["nonMachinable"] = True
    result = roulier.get("laposte_fr", "get_label", vals)
    assert sorted(result.keys()), ["annexes", "parcels"]
    print(_print_label_with_labelary_dot_com(result))

    parcel = result["parcels"][0]
    assert sorted(parcel.keys()), ["id", "label", "reference", "tracking"]


def test_misc_product():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DOS"
    result = roulier.get("laposte_fr", "get_label", vals)
    assert result.get("parcels"), True


def test_common_failed_get_label():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "COL"
    # Weight
    vals["parcels"][0]["weight"] = 35
    with pytest.raises(CarrierError, match="Le poids du colis est incorrect"):
        roulier.get("laposte_fr", "get_label", vals)
    vals["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError, match="Le poids du colis n'a pas été transmis"):
        roulier.get("laposte_fr", "get_label", vals)
        vals["parcels"][0]["weight"] = DATA["parcels"][0]["weight"]
    # country
    old = "FR"
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        del vals["from_address"]["country"]
        roulier.get("laposte_fr", "get_label", vals)
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        vals["from_address"]["country"] = old
        del vals["to_address"]["country"]
        roulier.get("laposte_fr", "get_label", vals)
        vals["to_address"]["country"] = old


def _do_not_execute_test_on_remote():
    """ Test execution require valid credentials
        which are not included in commited files.

        Main tests are only executable in local installation.
    """
    if DATA["auth"]["password"] == "blablabla":
        return True
    return False


def _print_label_with_labelary_dot_com(result):
    if not DOWNLOAD_PDF_FILE:
        return
    url = "http://api.labelary.com/v1/printers/8dpmm/labels/4x6/%s"
    headers = {"Accept": "application/pdf"}
    for parcel in result.get("parcels"):
        if parcel.get("label") and parcel["label"].get("data"):
            zpl = base64.b64decode(parcel["label"]["data"]).decode("utf8")
            response = requests.post(
                url % parcel.get("id"),
                headers=headers,
                files={"file": zpl},
                stream=True,
            )
            if response.status_code == 200:
                response.raw.decode_content = True
                with open("label%s.png" % parcel.get("id"), "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                    print("label %s downloaded" % parcel.get("id"))
            else:
                print("Error: " + response.text)
