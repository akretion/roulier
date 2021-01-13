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
from ..constants import SERVICE_FDS
from ..constants import SERVICE_SHD
from ..constants import SERVICE_SRS

logger = logging.getLogger(__name__)

EXCEPTION_MESSAGE = "Failed call with parameters %s"


def test_methods():
    assert (
        "gls_eu" in roulier.get_carriers_action_available().keys()
    ), "GLS EU carrier unavailable"
    assert roulier.get_carriers_action_available()["gls_eu"] == [
        "get_label",
    ], "get_label() method unavailable"


def test_label_basic_checks():
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "whatisitproduct"

    with pytest.raises(InvalidApiInput, match="unallowed value whatisitproduct"):
        roulier.get("gls_eu", "get_label", vals)

    del vals["service"]["product"]
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_language_get_label():
    vals = copy.deepcopy(DATA)
    # Weight
    vals["parcels"][0]["weight"] = 99.99
    with pytest.raises(CarrierError, match="weight exceeds"):
        roulier.get("gls_eu", "get_label", vals)

    vals["service"]["language"] = "fr"
    with pytest.raises(CarrierError, match="poids dépasse"):
        roulier.get("gls_eu", "get_label", vals)


def test_common_failed_get_label():
    vals = copy.deepcopy(DATA)
    # Weight
    vals["parcels"][0]["weight"] = 99.99
    with pytest.raises(CarrierError, match="weight exceeds"):
        roulier.get("gls_eu", "get_label", vals)

    vals["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError, match="define a weight"):
        roulier.get("gls_eu", "get_label", vals)
        vals["parcels"][0]["weight"] = DATA["parcels"][0]["weight"]

    # Country
    vals["parcels"][0]["weight"] = 1
    vals["to_address"].pop("country")
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        roulier.get("gls_eu", "get_label", vals)

    vals["to_address"]["country"] = "42"
    with pytest.raises(CarrierError, match="'Country' in Delivery is not valid"):
        roulier.get("gls_eu", "get_label", vals)

    # no address
    del vals["to_address"]
    with pytest.raises(CarrierError, match="at least a delivery or pickup address"):
        roulier.get("gls_eu", "get_label", vals)


def test_auth():
    vals = copy.deepcopy(DATA)
    vals["auth"]["login"] = "test"
    with pytest.raises(CarrierError, match="0009"):
        roulier.get("gls_eu", "get_label", vals)


def test_eu_country():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["country"] = "DE"
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_FDS():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_FDS}]
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(vals, result, 1, 0)


# TODO: find a valid pickupLocationId, else Server Exception from GLS
# def test_SHD():
#     vals = copy.deepcopy(DATA)
#     vals["to_address"]["contact"] = "Dylann"
#     vals["parcels"][0]["services"] = [{"product": SERVICE_SHD, "pickupLocationId": "2501234567"}]
#     result = roulier.get("gls_eu", "get_label", vals)
#     assert_result(vals, result, 1, 0)


def test_SHD_auto():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["contact"] = "Dylann"
    vals["parcels"][0]["services"] = [{"product": SERVICE_SHD}]
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SRS():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_SRS}]
    with pytest.raises(CarrierError, match="is missing: Return Address"):
        roulier.get("gls_eu", "get_label", vals)
    vals["return_address"] = copy.deepcopy(vals["to_address"])
    with pytest.raises(CarrierError, match="is missing: Return parcel weight"):
        roulier.get("gls_eu", "get_label", vals)
    vals["returns"] = [{"weight": 1}]
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SRS_return_only():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_SRS}]
    vals["pickup_address"] = copy.deepcopy(vals["to_address"])
    vals["returns"] = [{"weight": 1}]
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(
        vals, result, 1, 0, False
    )  # no label: GLS will generate it inside the agency


def test_PandR():
    vals = copy.deepcopy(DATA)
    vals["pickup_address"] = vals.pop("to_address")
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(
        vals, result, 1, 0, False
    )  # no label: GLS will generate it inside the agency


def test_PandS():
    vals = copy.deepcopy(DATA)
    vals["pickup_address"] = copy.deepcopy(vals["to_address"])
    result = roulier.get("gls_eu", "get_label", vals)
    assert_result(
        vals, result, 1, 0, False
    )  # no label: GLS will generate it inside the agency


def assert_result(vals, result, parcels, annexes, label_type="PDF"):
    assert sorted(result.keys()) == ["annexes", "parcels"], EXCEPTION_MESSAGE % vals
    assert len(result["annexes"]) == annexes
    assert len(result["parcels"]) == parcels
    for parcel in result["parcels"]:
        assert_parcel(vals, parcel, label_type)


def assert_parcel(vals, parcel, label_type="PDF"):
    if label_type:
        expected = ["id", "label", "reference", "tracking"]
    else:
        expected = ["id", "reference", "tracking"]
    assert sorted(parcel.keys()) == expected, EXCEPTION_MESSAGE % vals
    assert sorted(parcel["tracking"].keys()) == ["number", "partner", "url"], (
        EXCEPTION_MESSAGE % vals
    )
    assert parcel["tracking"]["number"]
    assert parcel["tracking"]["url"]
    if label_type:
        assert_label(parcel, label_type)


def assert_label(parcel, label_type="PDF"):
    assert "label" in parcel
    assert "data" in parcel["label"]
    assert len(parcel["label"]["data"]) > 1024
    assert parcel["label"]["type"] == label_type
