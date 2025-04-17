# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from datetime import date
from roulier import roulier
from roulier.exception import InvalidApiInput
from base64 import b64decode
from ....helpers import merge
from ....tests.helpers import assert_pdf


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
                "product": "01002",
                "shippingDate": date(
                    2025, 4, 17
                ),  # Update the date when launching the tests with the credentials
            }
        },
    )


def before_record_response(response):
    if "Set-Cookie" in response["headers"]:
        del response["headers"]["Set-Cookie"]
    if "Content-Disposition" in response["headers"]:
        del response["headers"]["Content-Disposition"]
    return response


@pytest.mark.vcr(
    filter_post_data_parameters=["USER_COMPTE", "USER_PASSWORD"],
    filter_query_parameters=["expediteur", "liste_cmd"],
    filter_headers=["Cookie"],
    before_record_response=before_record_response,
)
def test_ciblex_label_pdf(get_label_data):
    rv = roulier.get("ciblex", "get_label", get_label_data)
    assert "parcels" in rv
    assert rv["parcels"][0]["id"]

    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")


@pytest.mark.vcr(
    filter_post_data_parameters=["USER_COMPTE", "USER_PASSWORD"],
    filter_query_parameters=["expediteur", "liste_cmd"],
    filter_headers=["Cookie"],
    before_record_response=before_record_response,
)
def test_ciblex_label_epl(get_label_data):
    data = get_label_data
    data["service"]["labelFormat"] = "EPL"
    rv = roulier.get("ciblex", "get_label", data)
    assert "parcels" in rv
    assert rv["parcels"][0]["id"]

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
        match="to_address.street1\n  String should have at most 40 characters",
    ):
        roulier.get("ciblex", "get_label", data)


@pytest.mark.vcr(
    filter_post_data_parameters=["USER_COMPTE", "USER_PASSWORD"],
    filter_query_parameters=["expediteur", "liste_cmd"],
    filter_headers=["Cookie"],
    before_record_response=before_record_response,
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
    assert rv["parcels"][0]["id"]
    assert rv["parcels"][1]["id"]

    assert rv["parcels"][0]["label"]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == "PDF"
    assert_pdf(label["data"])

    assert not rv["parcels"][1]["label"]

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")

    assert "tracking" in rv["parcels"][1]
    tracking = rv["parcels"][1]["tracking"]
    assert tracking["number"]
    assert tracking["url"].startswith("https://secure.extranet.ciblex.fr")

    assert tracking["number"] != rv["parcels"][0]["tracking"]["number"]
