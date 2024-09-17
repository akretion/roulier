# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import pytest
import time
from datetime import date
from pathlib import Path
from roulier import roulier
from ....helpers import merge
from ....tests.helpers import assert_data_type, assert_pdf
from ....exception import CarrierError, InvalidApiInput


@pytest.fixture
def get_label_data(credentials, base_get_label_data):
    return merge(
        credentials["colissimo_fr"],
        base_get_label_data,
        {
            "service": {
                "product": "COL",
                "shippingDate": date(2025, 1, 1),
            }
        },
    )


@pytest.fixture
def packing_slip_data(credentials):
    return merge(
        credentials["colissimo_fr"],
    )


@pytest.fixture
def document_data(credentials):
    return merge(
        {
            "service": {
                "account_number": "xxxxx",
            },
        },
        credentials["colissimo_fr"],
        {"service": {}},
    )


def before_record_request(request):
    if request.body and request.headers.get("Content-Type") == "application/json":
        body = json.loads(request.body.decode("utf-8"))
        if "credential" in body:
            for key in [
                "apiKey",
                "login",
                "password",
            ]:
                if key in body["credential"]:
                    body["credential"][key] = "xxxx"
        if "contractNumber" in body:
            body["contractNumber"] = "xxxx"
        if "accountNumber" in body:
            body["accountNumber"] = "xxxx"
        if "password" in body:
            body["password"] = "xxxx"
        request.body = json.dumps(body).encode("utf-8")
    return request


def assert_label(rv, label_type="PDF"):
    assert "parcels" in rv
    assert rv["parcels"][0]["id"]

    assert "label" in rv["parcels"][0]
    label = rv["parcels"][0]["label"]
    assert label["name"] == "label"
    assert label["type"] == f"{label_type}"
    assert_data_type(label["data"], label_type[:3])


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_colissimo_label(get_label_data):
    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_colissimo_label_zpl(get_label_data):
    get_label_data["service"]["labelFormat"] = "ZPL"
    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(rv, "ZPL")


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_colissimo_bad_product(get_label_data):
    get_label_data["service"]["product"] = "INVALID_PRODUCT"
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("colissimo_fr", "get_label", get_label_data)

    assert excinfo.value.args[0][0]["id"] == 30109
    assert excinfo.value.args[0][0]["message"] == (
        "Le pays ou code postal expéditeur ne permet pas d’effectuer un envoi"
    )


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_1(get_label_data):
    get_label_data["parcels"][0]["weight"] = 35
    with pytest.raises(CarrierError, match="Le poids du colis est incorrect"):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_2(get_label_data):
    get_label_data["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError, match="Le poids du colis n'a pas été transmis"):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_3(get_label_data):
    del get_label_data["from_address"]["country"]
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("colissimo_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "from_address.country\n  Field required" in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_common_failed_get_label_4(get_label_data):
    del get_label_data["to_address"]["country"]
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("colissimo_fr", "get_label", get_label_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "to_address.country\n  Field required" in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_pickup_fail_1(get_label_data):
    get_label_data["service"]["product"] = "BPR"
    get_label_data["to_address"]["email"] = "no-reply@webu.coop"
    get_label_data["service"]["pickupLocationId"] = "929750"
    get_label_data["service"]["commercialName"] = "Webu"
    del get_label_data["to_address"]["phone"]

    with pytest.raises(CarrierError, match="'id': 30220,"):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_pickup_fail_2(get_label_data):
    get_label_data["service"]["product"] = "BPR"
    get_label_data["to_address"]["email"] = "no-reply@webu.coop"
    get_label_data["service"]["pickupLocationId"] = "929750"
    get_label_data["service"]["commercialName"] = "Webu"
    del get_label_data["to_address"]["phone"]
    get_label_data["to_address"]["landlinePhone"] = "0123456789"

    with pytest.raises(CarrierError, match="'id': 30220,"):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_pickup_ok(get_label_data):
    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.block_network
def test_packing_slip_missing_fields(packing_slip_data):
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("colissimo_fr", "get_packing_slip", packing_slip_data)

    assert "Invalid input data" in str(excinfo.value)
    assert (
        "Value error, At least one of packing_slip_number or parcels_numbers "
        "is required"
    ) in str(excinfo.value)


@pytest.mark.block_network
def test_packing_slip_both_fields(packing_slip_data):
    packing_slip_data["parcels_numbers"] = ["123", "456"]
    packing_slip_data["packing_slip_number"] = "123"

    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("colissimo_fr", "get_packing_slip", packing_slip_data)

    assert (
        "Value error, Only one of packing_slip_number or parcels_numbers is allowed"
    ) in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_packing_slip_unknown_parcel(get_label_data):
    get_label_data["parcels_numbers"] = ["unknown", "missing"]
    with pytest.raises(CarrierError) as excinfo:
        roulier.get("colissimo_fr", "get_packing_slip", get_label_data)

    assert "50031" in str(excinfo.value)
    assert "Numéro de colis invalide" in str(excinfo.value)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_common_success_get_packing_slip(get_label_data, packing_slip_data):
    get_label_data["parcels"][0]["nonMachinable"] = True
    result = roulier.get("colissimo_fr", "get_label", get_label_data)

    # now we can get the packing slip for this parcel
    packing_slip_data["parcels_numbers"] = [
        p["tracking"]["number"] for p in result["parcels"]
    ]
    res = roulier.get("colissimo_fr", "get_packing_slip", packing_slip_data)

    assert res["packing_slip"].get("number")
    assert res["packing_slip"].get("number_of_parcels") == len(
        packing_slip_data["parcels_numbers"]
    )
    assert len(res["annexes"])
    assert_pdf(res["annexes"][0]["data"])


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_DOM_product(get_label_data):
    """France - Colissimo Domicile - sans signature"""
    get_label_data["service"]["product"] = "DOM"
    result = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(result)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_DOS_product(get_label_data):
    """France - Colissimo Domicile - avec signature"""
    get_label_data["service"]["product"] = "DOS"
    result = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(result)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_DOM_product_raise_1(get_label_data):
    """Test for invalid zip code"""
    get_label_data["service"]["product"] = "DOM"
    get_label_data["to_address"]["zip"] = "99999"
    with pytest.raises(
        CarrierError,
        match="Le code pays ou le code postal du destinataire est incorrect "
        "pour le code produit fourni",
    ):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_DOM_product_raise_2(get_label_data):
    """Test for invalid zip code"""
    get_label_data["service"]["product"] = "DOM"
    # 30108 = Le code postal de l'expéditeur ne correspond pas au pays
    get_label_data["to_address"]["zip"] = "21000"
    get_label_data["from_address"]["zip"] = "9999"
    with pytest.raises(CarrierError, match="30108"):
        roulier.get("colissimo_fr", "get_label", get_label_data)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_COM_product(get_label_data):
    """Outre-Mer - Colissimo Domicile - sans signature"""
    get_label_data["service"]["product"] = "COM"
    get_label_data["service"]["transportationAmount"] = 123
    get_label_data["service"]["totalAmount"] = 123
    get_label_data["to_address"]["country"] = "GP"  # Guadeloupe
    get_label_data["to_address"]["zip"] = "97100"  # Basse-Terre
    get_label_data["parcels"][0]["customs"] = {
        "articles": [
            {
                "quantity": "2",
                "weight": 0.5,
                "originCountry": "FR",
                "description": "Printed circuits",
                "hsCode": "853400",
                "value": 1.0,
            }
        ],
        "category": 3,
    }
    get_label_data["parcels"][0]["totalAmount"] = 123  # Frais de transport
    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.vcr(
    filter_headers=["apiKey"],
    before_record_request=before_record_request,
)
def test_full_customs_declarations(get_label_data):
    """Complete customsDeclarations"""
    get_label_data["service"]["product"] = "COM"
    get_label_data["to_address"]["country"] = "GP"  # Guadeloupe
    get_label_data["to_address"]["zip"] = "97100"  # Basse-Terre
    get_label_data["parcels"][0]["customs"] = {
        "articles": [
            {
                "description": "Printed circuits",
                "quantity": "2",
                "weight": 0.5,
                "value": 1.0,
                "hsCode": "853400",
                "originCountry": "FR",
                "currency": "EUR",
                "artref": "artref",
                "originalIdent": "A",
                "vatAmount": 0,
                "customsFees": 0,
            }
        ],
        "category": 3,
        "original": [
            {
                "originalIdent": "A",
                "originalInvoiceNumber": "111141111",
                "originalInvoiceDate": "2016-11-02",
                "originalParcelNumber": "7Q06270508932",
            }
        ],
        "importersReference": "",
        "importersContact": "",
        "officeOrigin": "",
        "comments": "comments",
        "description": "Fake description",
        "invoiceNumber": "111141111",
        "licenceNumber": "",
        "certificatNumber": "",
        "importerAddress": {
            "company": "company name",
            "name": "Lastname",
            "firstName": "Firstname",
            "street0": "line0",
            "street1": "line1",
            "street2": "line2",
            "street3": "line3",
            "country": "FR",
            "city": "city",
            "zip": "75007",
            "phone": "+12089145766",
            "mobile": "0600000007",
            "door1": "",
            "door2": "",
            "email": "email@email.fr",
            "intercom": "intercom",
            "language": "FR",
        },
    }
    get_label_data["service"]["totalAmount"] = 123  # Frais de transport

    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    assert_label(rv)


@pytest.mark.block_network
def test_documents_missing_parcel_number(document_data):
    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("colissimo_fr", "get_documents", document_data)

    assert "Invalid input data" in str(excinfo.value)
    assert "parcel_number\n  Field required" in str(excinfo.value)


@pytest.mark.vcr(
    before_record_request=before_record_request,
    filter_headers=["apiKey"],
)
def test_documents_ok(vcr, get_label_data, document_data):
    get_label_data = merge(
        get_label_data,
        {
            "service": {
                "product": "DOS",
                "transportationAmount": 123,
                "dematerialized": True,
                "totalAmount": 123,
            },
            "to_address": {
                "street1": "220 Bridge Ave",
                "city": "Allenwood",
                "country": "US",
                "stateOrProvinceCode": "PA",
                "zip": "17810",
                "phone": "+33612121212",
            },
        },
    )
    get_label_data["parcels"][0] = {
        **get_label_data["parcels"][0],
        "customs": {
            "articles": [
                {
                    "quantity": "2",
                    "weight": 0.5,
                    "originCountry": "FR",
                    "description": "Printed circuits",
                    "hsCode": "853400",
                    "value": 1.0,
                }
            ],
            "category": 3,
            "description": "Package",
        },
        "ddp": True,
        "length": 10,
        "width": 2,
        "height": 4,
    }

    rv = roulier.get("colissimo_fr", "get_label", get_label_data)
    parcel = rv["parcels"][0]

    document_data["service"]["parcel_number"] = parcel["tracking"]["number"]
    i = 0
    while True:
        try:
            rv = roulier.get("colissimo_fr", "get_documents", document_data)
        except CarrierError as e:
            if e.response is None or e.response.status_code != 404 or i > 300:
                raise
            i += 30
            if not vcr.play_count:  # Don't wait if we are in a VCR test
                time.sleep(30)
        else:
            break

    documents = rv["documents"]
    doc = [doc for doc in documents if doc["document_type"] == "CN23"]
    assert len(doc) == 1

    cn23_id = doc[0]["document_path"]
    document_data["service"]["document_id"] = cn23_id
    rv = roulier.get("colissimo_fr", "get_document", document_data)
    assert rv and "file" in rv
    assert_pdf(rv["file"])

    del document_data["service"]["document_id"]
    document_data["service"]["document_type"] = "COMMERCIAL_INVOICE"
    document_data["service"]["document_path"] = str(
        Path(__file__).parent / "test-facture.pdf"
    )
    rv = roulier.get("colissimo_fr", "create_document", document_data)
    doc_id = rv["document_id"]
    assert doc_id
