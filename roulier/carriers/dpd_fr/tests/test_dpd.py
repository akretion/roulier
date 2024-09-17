# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import pytest
from datetime import date
import re
from roulier import roulier
from ....helpers import merge
from ....tests.helpers import assert_data_type
from ....exception import CarrierError, InvalidApiInput


@pytest.fixture
def get_label_data(credentials, base_get_label_data):
    return merge(
        {
            "service": {
                "customerCountry": "XX",
                "customerId": "xxxxxx",
                "agencyId": "xx",
            },
        },
        credentials["dpd_fr"],
        base_get_label_data,
        {
            "service": {
                "product": "DPD_Classic",
                "shippingDate": date(
                    2025, 1, 1
                ),  # Update the date when launching the tests with the credentials
            }
        },
    )


def before_record_request(request):
    if request.body:
        body = request.body.decode("utf-8")
        for key in [
            "userid",
            "password",
            "customer_centernumber",
            "customer_number",
            "customer_countrycode",
        ]:
            body = re.sub(rf"<{key}>.*?</{key}>", f"<{key}>xxxx</{key}>", body)
        request.body = body.encode("utf-8")
    return request


def assert_label(rv, label_type="PDF"):
    assert "parcels" in rv
    assert rv["parcels"][0]["id"]

    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == f"{label_type} Label"
    assert label["type"] == f"{label_type}"
    assert_data_type(label["data"], label_type[:3])

    assert "tracking" in rv["parcels"][0]
    tracking = rv["parcels"][0]["tracking"]
    assert tracking["number"]


@pytest.mark.vcr(
    ignore_localhost=True,
    before_record_request=before_record_request,
)
def test_dpd_label(get_label_data):
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.block_network
def test_label_bad_input_1(get_label_data):
    get_label_data["service"]["product"] = "whatisitproduct"
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert "Invalid input data" in str(excinfo.value)
    assert (
        "service.product\n  "
        "Input should be 'DPD_Classic', 'DPD_Predict' or 'DPD_Relais'"
        in str(excinfo.value)
    )


@pytest.mark.block_network
def test_label_bad_input_2(get_label_data):
    get_label_data["parcels"][0].pop("weight")
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "weight\n  Field required" in str(excinfo.value)


@pytest.mark.block_network
def test_label_bad_input_3(get_label_data):
    get_label_data["to_address"].pop("country")
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "country\n  Field required" in str(excinfo.value)


@pytest.mark.block_network
def test_label_bad_input_4(get_label_data):
    del get_label_data["to_address"]
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "to_address\n  Field required" in str(excinfo.value)


@pytest.mark.block_network
def test_predict_fail_1(get_label_data):
    get_label_data["service"]["product"] = "DPD_Predict"

    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "Predict notifications must be set to Predict" in str(excinfo.value)


@pytest.mark.block_network
def test_predict_fail_2(get_label_data):
    get_label_data["service"]["product"] = "DPD_Predict"
    get_label_data["service"]["notifications"] = "wrong"

    with pytest.raises(InvalidApiInput) as excinfo:
        # , {"service": [{"notifications": "must be set to Predict"}]}
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert (
        "service.notifications\n  "
        "Input should be 'No', 'Predict', 'AutomaticSMS' or 'AutomaticMail"
    ) in str(excinfo.value)


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_predict_fail_3(get_label_data):
    get_label_data["service"]["product"] = "DPD_Predict"
    get_label_data["service"]["notifications"] = "Predict"

    # no mobile number
    del get_label_data["to_address"]["phone"]

    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)

    assert "no sms number given" in str(excinfo.value)


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_predict_ok(get_label_data):
    get_label_data["service"]["product"] = "DPD_Predict"
    get_label_data["service"]["notifications"] = "Predict"

    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_dpd_format_pdf(get_label_data):
    get_label_data["service"]["labelFormat"] = "PDF"
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_dpd_format_pdf_a6(get_label_data):
    get_label_data["service"]["labelFormat"] = "PDF_A6"
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv, "PDF_A6")


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_dpd_format_png(get_label_data):
    get_label_data["service"]["labelFormat"] = "PNG"
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv, "PNG")


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_dpd_format_zpl(get_label_data):
    get_label_data["service"]["labelFormat"] = "ZPL"
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv, "ZPL")


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_dpd_format_epl(get_label_data):
    get_label_data["service"]["labelFormat"] = "EPL"
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv, "EPL")


@pytest.mark.block_network
def test_dpd_format_invalid(get_label_data):
    get_label_data["service"]["labelFormat"] = "invalid"
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert "Invalid input data" in str(excinfo.value)
    assert (
        "service.labelFormat\n  "
        "Input should be 'PNG', 'PDF', 'PDF_A6', 'ZPL', 'ZPL300', 'ZPL_A6', "
        "'ZPL300_A6' or 'EPL'" in str(excinfo.value)
    )


@pytest.mark.vcr(
    before_record_request=before_record_request,
    allow_localhost=True,
)
def test_common_failed_get_label_1(get_label_data):
    # Weight
    get_label_data["parcels"][0]["weight"] = 999.99
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert excinfo.value.args[0][0]["id"] == "InvalidWeight"


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_common_failed_get_label_2(get_label_data):
    get_label_data["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert excinfo.value.args[0][0]["id"] == "InvalidWeight"


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_common_failed_get_label_3(get_label_data):
    get_label_data["to_address"]["country"] = "ZZ"
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert excinfo.value.args[0][0]["id"] == "InvalidCountryPrefix"


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_auth(get_label_data):
    get_label_data["auth"]["login"] = "test"
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert excinfo.value.args[0][0]["id"] == "PermissionDenied"


@pytest.mark.block_network
def test_relai_fail(get_label_data):
    get_label_data["service"]["product"] = "DPD_Relais"
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dpd_fr", "get_label", get_label_data)
    assert "Invalid input data" in str(excinfo.value)
    assert "service\n  Value error, pickupLocationId is mandatory for Relais" in str(
        excinfo.value
    )


@pytest.mark.vcr(
    before_record_request=before_record_request,
)
def test_relai_ok(get_label_data):
    get_label_data["service"]["product"] = "DPD_Relais"
    get_label_data["service"]["pickupLocationId"] = "P32500"  # Simon Services
    rv = roulier.get("dpd_fr", "get_label", get_label_data)
    assert_label(rv)
