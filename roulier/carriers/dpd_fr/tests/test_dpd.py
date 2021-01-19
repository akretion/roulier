# -*- coding: utf-8 -*-
import logging
import copy
import base64
import requests
import shutil
import pytest
import re

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA

logger = logging.getLogger(__name__)


EXCEPTION_MESSAGE = "Failed call with parameters %s"


def test_methods():
    assert (
        "dpd_fr" in roulier.get_carriers_action_available().keys()
    ), "DPD carrier unavailable"
    assert roulier.get_carriers_action_available()["dpd_fr"] == [
        "get_label",
    ], "get_label() method unavailable"


def test_label_basic_checks():
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "whatisitproduct"

    with assert_raises(InvalidApiInput, {"service": [{"product": "unallowed"}]}):
        roulier.get("dpd_fr", "get_label", vals)

    del vals["service"]["product"]
    result = roulier.get("dpd_fr", "get_label", vals)
    assert_result(vals, result, 1, 1)


def test_common_failed_get_label():
    vals = copy.deepcopy(DATA)
    # Weight
    orig_weight = vals["parcels"][0].pop("weight")
    with assert_raises(InvalidApiInput, {"parcels": [{0: [{"weight": "float"}]}]}):
        roulier.get("dpd_fr", "get_label", vals)

    vals["parcels"][0]["weight"] = 999.99
    with assert_raises(CarrierError, "Invalid weight"):
        roulier.get("dpd_fr", "get_label", vals)

    vals["parcels"][0]["weight"] = 0
    with assert_raises(CarrierError, "Invalid weight"):
        roulier.get("dpd_fr", "get_label", vals)
    vals["parcels"][0]["weight"] = orig_weight

    # Country
    vals["to_address"].pop("country")
    with assert_raises(InvalidApiInput, {"to_address": [{"country": "empty"}]}):
        roulier.get("dpd_fr", "get_label", vals)

    vals["to_address"]["country"] = "ZZ"
    with assert_raises(CarrierError, [{"id": "InvalidCountryPrefix"}]):
        roulier.get("dpd_fr", "get_label", vals)

    # no address
    del vals["to_address"]
    with assert_raises(InvalidApiInput, {"to_address": "empty"}):
        roulier.get("dpd_fr", "get_label", vals)


def test_auth():
    vals = copy.deepcopy(DATA)
    vals["auth"]["login"] = "test"
    with assert_raises(CarrierError, [{"id": "PermissionDenied"}]):
        roulier.get("dpd_fr", "get_label", vals)


def test_relai():
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "DPD_Relais"
    with assert_raises(
        InvalidApiInput, {"service": [{"pickupLocationId": "mandatory"}]}
    ):
        roulier.get("dpd_fr", "get_label", vals)
    vals["service"]["pickupLocationId"] = "P62025"
    result = roulier.get("dpd_fr", "get_label", vals)
    assert_result(vals, result, 1, 1)


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
    if label_type:
        assert_label(parcel, label_type)


def assert_label(parcel, label_type="PDF"):
    assert "label" in parcel
    assert "data" in parcel["label"]
    assert len(parcel["label"]["data"]) > 1024
    assert parcel["label"]["type"] == label_type


class assert_raises(object):
    def __init__(self, exc_type, expected=None):
        self.expected = expected
        self.exc_type = exc_type

    def _check_expected(self, errors, expected):
        if isinstance(expected, str):
            error_repr = "%s" % errors
            assert re.search(expected, error_repr), "invalid inputs are not as expected"
            return
        assert type(errors) == type(expected)
        if isinstance(expected, list):
            assert len(errors) >= len(expected), "invalid inputs are not as expected"
            keys = range(0, len(expected))
        elif isinstance(expected, dict):
            error_keys = set(errors.keys())
            expected_keys = set(expected.keys())
            assert not expected_keys - error_keys, "invalid inputs are not as expected"
            keys = expected_keys
        else:
            raise ValueError("invalid expected format")
        for k in keys:
            if expected is not None:
                self._check_expected(errors[k], expected[k])

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, traceback):
        assert exc_type == self.exc_type
        if self.expected:
            if self.exc_type == InvalidApiInput:
                errors = exc_val.args[0]["api_call_exception"]
            else:
                errors = exc_val.args[0]
            self._check_expected(errors, self.expected)
        return True
