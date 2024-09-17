# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from datetime import date
from roulier import roulier
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
                    2024, 12, 1
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
def test_ciblex_label(get_label_data):
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
