# -*- coding: utf-8 -*-
import logging
import copy
import base64
import requests
import shutil
import pytest

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA, PACKING_SLIP_DATA

logger = logging.getLogger(__name__)

DOWNLOAD_PDF_FILE = False  # Update to get demo files

EXCEPTION_MESSAGE = "Failed call with parameters %s"


def test_methods():
    assert (
        "laposte_fr" in roulier.get_carriers_action_available().keys()
    ), "Laposte carrier unavailable"
    assert roulier.get_carriers_action_available()["laposte_fr"] == [
        "get_label",
        "get_packing_slip",
    ], "get_label() or get_packing_slip() methods unavailable"


def test_label_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        roulier.get("laposte_fr", "get_label", DATA)
    vals = copy.deepcopy(DATA)

    vals["service"]["product"] = "whatisitproduct"
    with pytest.raises(CarrierError, match="'id': 30109"):
        roulier.get("laposte_fr", "get_label", vals)

    vals["service"]["product"] = "COL"
    vals["parcels"][0]["nonMachinable"] = True
    result = roulier.get("laposte_fr", "get_label", vals)
    assert sorted(result.keys()) == ["annexes", "parcels"], EXCEPTION_MESSAGE % vals
    print(_print_label_with_labelary_dot_com(result))

    parcel = result["parcels"][0]
    assert sorted(parcel.keys()) == ["id", "label", "reference", "tracking"], (
        EXCEPTION_MESSAGE % vals
    )


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


def test_auth():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(DATA)
    vals["auth"]["login"] = "test"
    vals["service"]["product"] = "COL"
    with pytest.raises(CarrierError, match="Identifiant ou mot de passe incorrect"):
        roulier.get("laposte_fr", "get_label", vals)


def test_packing_slip_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PACKING_SLIP_DATA)
    regex = r".*((packing_slip_number|parcels_numbers)': \['required field'.*){2}"
    with pytest.raises(InvalidApiInput, match=regex):
        roulier.get("laposte_fr", "get_packing_slip", vals)

    vals["parcels_numbers"] = ["123", "456"]
    vals["packing_slip_number"] = "123"
    regex = r"'parcels_numbers' must not be present with 'packing_slip_number'"
    with pytest.raises(InvalidApiInput, match=regex):
        roulier.get("laposte_fr", "get_packing_slip", vals)


def test_common_failed_get_packing_slip():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PACKING_SLIP_DATA)

    vals["parcels_numbers"] = ["123", "456"]
    regex = r"'id': 50031"  # numéro de colis invalide
    with pytest.raises(CarrierError, match=regex):
        roulier.get("laposte_fr", "get_packing_slip", vals)

    del vals["parcels_numbers"]
    vals["packing_slip_number"] = "0"
    regex = r"'id': 50027"  # not found
    with pytest.raises(CarrierError, match=regex):
        roulier.get("laposte_fr", "get_packing_slip", vals)


def test_common_success_get_packing_slip():
    if _do_not_execute_test_on_remote():
        return
    # first, we need to create a valid parcel number
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "COL"
    vals["parcels"][0]["nonMachinable"] = True
    result = roulier.get("laposte_fr", "get_label", vals)

    # now we can get the packing slip for this parcel
    vals = copy.deepcopy(PACKING_SLIP_DATA)
    vals["parcels_numbers"] = [p["tracking"]["number"] for p in result["parcels"]]
    res = roulier.get("laposte_fr", "get_packing_slip", vals)

    assert res["packing_slip"].get("number")
    assert res["packing_slip"].get("number_of_parcels") == len(vals["parcels_numbers"])

    # now we can get the packing slip with it's ID
    vals = copy.deepcopy(PACKING_SLIP_DATA)
    vals["packing_slip_number"] = res["packing_slip"]["number"]
    new_res = roulier.get("laposte_fr", "get_packing_slip", vals)

    # we sould get the same result: it's not a newly generated document.
    assert res == new_res


def _do_not_execute_test_on_remote():
    """Test execution require valid credentials
    which are not included in commited files.

    Main tests are only executable in local installation.
    This method when called allow to escape remote tests
    """
    if DATA["auth"]["password"] == "blablabla":
        return True
    return False


def _print_label_with_labelary_dot_com(result):
    """This method convert zpl data in pdf file"""
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


def assert_label(result):
    assert "parcels" in result
    assert len(result["parcels"]) > 0
    assert "label" in result["parcels"][0]
    assert "data" in result["parcels"][0]["label"]
    return result["parcels"][0]["label"]
