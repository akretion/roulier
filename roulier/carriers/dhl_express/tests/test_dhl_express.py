# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from datetime import datetime

import pytest

from roulier import roulier

from ....exception import CarrierError, InvalidApiInput
from ....helpers import merge
from ....tests.helpers import assert_data_type

shipping_date = datetime(2026, 2, 13)


@pytest.fixture
def get_label_data(credentials, base_get_label_data):
    data = merge(
        credentials["dhl_express"],
        base_get_label_data,
        {
            "service": {
                "product": "N",
                "shippingDate": shipping_date,
                "shipment_description": "Test DHL Express",
                "reference1": "Ref1",
            }
        },
    )
    for parcel in data["parcels"]:
        parcel["width"] = 10
        parcel["length"] = 10
        parcel["height"] = 10
    return data


def before_record_request(request):
    if request.body and request.headers.get("Content-Type") == "application/json":
        body = json.loads(request.body.decode("utf-8"))
        if "accounts" in body:
            for account in body["accounts"]:
                if "number" in account:
                    account["number"] = "xxxx"
        request.body = json.dumps(body).encode("utf-8")
    return request


def assert_label(rv, label_type="PDF", i=0):
    assert "parcels" in rv
    assert rv["parcels"][i]["id"]

    assert "label" in rv["parcels"][i]
    label = rv["parcels"][i]["label"]
    assert label["name"] == "label"
    assert label["type"] == f"{label_type}"
    assert_data_type(label["data"], label_type[:3])


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_dhl_express_label(get_label_data):
    rv = roulier.get("dhl_express", "get_label", get_label_data)
    assert_label(rv)
    assert rv["parcels"][0]["reference"] == get_label_data["parcels"][0]["reference"]


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
    ignore_localhost=True,
)
def test_dhl_express_multi_label(get_label_data):
    data = get_label_data
    data["parcels"].append(
        {
            "weight": 2.5,
            "reference": "Parcel 2",
            "width": 10,
            "length": 10,
            "height": 10,
        },
    )
    rv = roulier.get("dhl_express", "get_label", data)
    assert_label(rv)
    assert_label(rv, i=1)
    assert rv["parcels"][0]["reference"] == "Parcel 1"
    assert rv["parcels"][1]["reference"] == "Parcel 2"


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_dhl_express_label_zpl(get_label_data):
    get_label_data["service"]["labelFormat"] = "ZPL"
    rv = roulier.get("dhl_express", "get_label", get_label_data)
    assert_label(rv, "ZPL")


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_dhl_express_bad_product(get_label_data):
    get_label_data["service"]["product"] = "?"
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dhl_express", "get_label", get_label_data)

    assert excinfo.value.args[0][0]["id"] == 8007
    assert excinfo.value.args[0][0]["message"] == (
        "Bad request (Error getting Product details from GREF)"
    )


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_1(get_label_data):
    get_label_data["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError, match="0.0 is not greater or equal to 0.001"):
        roulier.get("dhl_express", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_2(get_label_data):
    del get_label_data["from_address"]["country"]
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dhl_express", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "from_address.country\n  Field required" in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_3(get_label_data):
    del get_label_data["to_address"]["country"]
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dhl_express", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "to_address.country\n  Field required" in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_pickup_ok(get_label_data):
    get_label_data["service"]["pickupLocationId"] = "On the floor"
    rv = roulier.get("dhl_express", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.vcr(
    filter_headers=["Authorization"],
    before_record_request=before_record_request,
)
def test_full_customs_declarations(get_label_data):
    """Complete customsDeclarations"""
    get_label_data["service"]["product"] = "P"
    get_label_data["to_address"]["country"] = "GP"  # Guadeloupe
    get_label_data["to_address"]["zip"] = "97100"  # Basse-Terre

    get_label_data["customs"] = {
        "invoice": {
            "number": "INV-123",
            "date": shipping_date.date(),
            "type": "gif",
            "content": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
        },
        "articles": [
            {
                "description": "Printed circuits",
                "quantity": 2,
                "weight": 0.5,
                "value": 1.0,
                "hsCode": "853400",
                "originCountry": "FR",
            }
        ],
        "vat": 0,
        "delivery": 123,
    }

    rv = roulier.get("dhl_express", "get_label", get_label_data)
    assert_label(rv)
