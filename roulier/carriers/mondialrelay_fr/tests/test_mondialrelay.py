# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from roulier import roulier
from datetime import time
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
def search_pickup_sites_data(credentials, base_search_pickup_site_data):
    return merge(
        credentials["mondialrelay_fr"],
        base_search_pickup_site_data,
    )


@pytest.fixture
def get_pickup_site_data(credentials, base_get_pickup_site_data):
    return merge(
        credentials["mondialrelay_fr"],
        base_get_pickup_site_data,
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
def test_mondialrelay_search_pickup_site(search_pickup_sites_data):
    rv = roulier.get("mondialrelay_fr", "search_pickup_sites", search_pickup_sites_data)
    assert "sites" in rv
    assert len(rv["sites"]) > 0
    site = rv["sites"][0]
    assert site["id"] == "005680"
    assert site["name"] == "BUREAU COPY"
    assert site["street"] == "31 COURS ANDRE PHILIP"
    assert site["zip"] == "69100"
    assert site["city"] == "VILLEURBANNE"
    assert site["country"] == "FR"
    assert site["lat"] == "45.7728450"
    assert site["lng"] == "04.8630410"
    assert len(site["hours"]) == 7
    assert site["hours"]["monday"]
    assert site["hours"]["monday"][0]["start"] == time(9, 0)
    assert site["hours"]["monday"][0]["end"] == time(12, 30)
    assert site["hours"]["monday"][1]["start"] == time(14, 0)
    assert site["hours"]["monday"][1]["end"] == time(18, 30)


@pytest.mark.vcr()
def test_mondialrelay_get_pickup_site(get_pickup_site_data):
    get_pickup_site_data["get"]["id"] = "005680"
    rv = roulier.get("mondialrelay_fr", "get_pickup_site", get_pickup_site_data)
    assert rv["site"]
    site = rv["site"]
    assert site["id"] == "005680"
    assert site["name"] == "BUREAU COPY"
    assert site["street"] == "31 COURS ANDRE PHILIP"
    assert site["zip"] == "69100"
    assert site["city"] == "VILLEURBANNE"
    assert site["country"] == "FR"
    assert site["lat"] == "45.7728450"
    assert site["lng"] == "04.8630410"
    assert len(site["hours"]) == 7
    assert site["hours"]["monday"]
    assert site["hours"]["monday"][0]["start"] == time(9, 0)
    assert site["hours"]["monday"][0]["end"] == time(12, 30)
    assert site["hours"]["monday"][1]["start"] == time(14, 0)
    assert site["hours"]["monday"][1]["end"] == time(18, 30)
