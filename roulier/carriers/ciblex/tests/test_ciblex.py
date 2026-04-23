# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode
from datetime import date

import pytest

from roulier import roulier
from roulier.exception import InvalidApiInput

from ....helpers import merge
from ....tests.helpers import assert_in_pdf, assert_pdf


@pytest.fixture
def get_label_data(credentials, base_get_label_data):
    return merge(
        {
            "service": {
                "customerId": "xxxxx",
                "product": "xxxxx",
            }
        },
        credentials["ciblex"],
        base_get_label_data,
        {
            "service": {
                "shippingDate": date(2025, 5, 16),
            }
        },
    )


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
)
def test_ciblex_label_pdf(get_label_data):
    rv = roulier.get("ciblex", "get_label", get_label_data)
    assert "parcels" in rv

    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(label["data"], "Parcel 1", "1.2 Kg")

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
)
def test_ciblex_label_epl(get_label_data):
    data = get_label_data
    data["service"]["labelFormat"] = "EPL"
    rv = roulier.get("ciblex", "get_label", data)
    assert "parcels" in rv

    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "EPL"
    # EPL: No magic bytes, just test a part of it
    assert label["data"]
    assert b"--- CB_2D ----" in b64decode(label["data"])

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")


@pytest.mark.block_network
def test_ciblex_label_bad_street(get_label_data):
    data = get_label_data
    data["to_address"]["street1"] = "23 rue de la République 75001 Paris CEDEX 129832Z"

    with pytest.raises(
        InvalidApiInput,
        match="to_address.street1\n  String should have at most 35 characters",
    ):
        roulier.get("ciblex", "get_label", data)


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
    ignore_hosts=["localhost"],
)
def test_ciblex_multi_package_to_label_pdf(get_label_data):
    data = get_label_data
    data["parcels"].append(
        {"weight": 2.5, "reference": "Parcel 2"},
    )
    rv = roulier.get("ciblex", "get_label", data)
    assert "parcels" in rv
    assert len(rv["parcels"]) == 2
    assert rv["parcels"][0]
    assert rv["parcels"][1]

    assert rv["parcels"][0]["label"]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(label["data"], "Parcel 1", "1.2 Kg", "1 / 2")

    assert rv["parcels"][1]["label"]
    label = rv["parcels"][1]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(label["data"], "Parcel 2", "2.5 Kg", "2 / 2")

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")

    assert "tracking" in rv["parcels"][1]
    tracking = rv["parcels"][1]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")

    assert tracking["number"] != rv["parcels"][0]["tracking"]["number"]


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
)
def test_ciblex_name_and_company(get_label_data):
    data = get_label_data
    data["to_address"]["company"] = "Akrétion Sarl Coop 792377731"
    del data["to_address"]["phone"]
    rv = roulier.get("ciblex", "get_label", data)

    assert rv["parcels"][0]["label"]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(
        label["data"],
        "Hugo Victor",
        "Akretion Sarl Coop 792377731",
        "6 Place des Vosges",
        "75004 Paris",
    )


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
)
def test_ciblex_phone(get_label_data):
    data = get_label_data
    data["to_address"]["phone"] = "+33123456789"
    rv = roulier.get("ciblex", "get_label", data)

    assert rv["parcels"][0]["label"]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(
        label["data"],
        "Hugo Victor",
        "33123456789",
        "6 Place des Vosges",
        "75004 Paris",
    )


@pytest.mark.vcr(
    filter_query_parameters=["i", "k", "exp_code", "contrat"],
)
def test_ciblex_name_and_company_and_phone(get_label_data):
    data = get_label_data
    data["to_address"]["company"] = "Akrétion Sarl Coop 792377731"
    data["to_address"]["phone"] = "+33123456789"
    rv = roulier.get("ciblex", "get_label", data)

    assert rv["parcels"][0]["label"]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])
    assert_in_pdf(
        label["data"],
        "Hugo Victor",
        "Akretion Sarl Coop 792377731",
        "33123456789",
        "6 Place des Vosges",
        "75004 Paris",
    )
