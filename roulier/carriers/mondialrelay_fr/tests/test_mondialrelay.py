# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from roulier import roulier
from ....helpers import merge


@pytest.fixture
def get_label_data(credentials, base_get_label_data):
    return merge(
        credentials["mondialrelay_fr"],
        base_get_label_data,
        {
            "service": {
                "product": "HOM",
                "pickupMode": "REL",
                "pickupSite": "AUTO",
                "pickupCountry": "FR",
            }
        },
    )


@pytest.fixture
def find_pickup_site_data(credentials, base_find_pickup_site_data):
    return merge(
        credentials["mondialrelay_fr"],
        base_find_pickup_site_data,
    )


@pytest.mark.vcr()
def test_mondialrelay_label(get_label_data):
    rv = roulier.get("mondialrelay_fr", "get_label", get_label_data)
    assert "parcels" in rv
    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label_url"
    assert label["type"] == "url"
    assert label["data"].startswith("https://www.mondialrelay.com")


@pytest.mark.vcr()
def test_mondialrelay_label_return(get_label_data):
    rv = roulier.get(
        "mondialrelay_fr",
        "get_label",
        merge(
            get_label_data,
            {
                "service": {
                    "product": "LCC",
                },
            },
        ),
    )
    assert "parcels" in rv
    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label_url"
    assert label["type"] == "url"
    assert label["data"].startswith("https://www.mondialrelay.com")


@pytest.mark.vcr()
def test_mondialrelay_pickup_site(find_pickup_site_data):
    rv = roulier.get("mondialrelay_fr", "find_pickup_site", find_pickup_site_data)
    assert "sites" in rv
    assert len(rv["sites"]) > 0
    assert "name" in rv["sites"][0]
