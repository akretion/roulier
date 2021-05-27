import base64
import copy
import logging
import pytest
import requests
import shutil

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
        "gls_fr_rest" in roulier.get_carriers_action_available().keys()
    ), "GLS EU carrier unavailable"
    assert roulier.get_carriers_action_available()["gls_fr_rest"] == [
        "get_label",
    ], "get_label() method unavailable"


def test_label_basic_checks():
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "whatisitproduct"

    with pytest.raises(InvalidApiInput, match="unallowed value whatisitproduct"):
        roulier.get("gls_fr_rest", "get_label", vals)

    del vals["service"]["product"]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_language_get_label():
    vals = copy.deepcopy(DATA)
    # Weight
    vals["parcels"][0]["weight"] = 99.99
    with pytest.raises(CarrierError, match="weight exceeds"):
        roulier.get("gls_fr_rest", "get_label", vals)

    vals["service"]["language"] = "fr"
    with pytest.raises(CarrierError, match="poids dépasse"):
        roulier.get("gls_fr_rest", "get_label", vals)


def test_common_failed_get_label():
    vals = copy.deepcopy(DATA)
    # Weight
    vals["parcels"][0]["weight"] = 99.99
    with pytest.raises(CarrierError, match="weight exceeds"):
        roulier.get("gls_fr_rest", "get_label", vals)

    vals["parcels"][0]["weight"] = 0
    with pytest.raises(CarrierError, match="define a weight"):
        roulier.get("gls_fr_rest", "get_label", vals)
        vals["parcels"][0]["weight"] = DATA["parcels"][0]["weight"]

    # Country
    vals["parcels"][0]["weight"] = 1
    vals["to_address"].pop("country")
    with pytest.raises(InvalidApiInput, match="empty values not allowed"):
        roulier.get("gls_fr_rest", "get_label", vals)

    vals["to_address"]["country"] = "42"
    with pytest.raises(CarrierError, match="'Country' in Delivery is not valid"):
        roulier.get("gls_fr_rest", "get_label", vals)

    # no address
    del vals["to_address"]
    with pytest.raises(CarrierError, match="at least a delivery or pickup address"):
        roulier.get("gls_fr_rest", "get_label", vals)


def test_auth():
    vals = copy.deepcopy(DATA)
    vals["auth"]["login"] = "test"
    with pytest.raises(CarrierError, match="0009"):
        roulier.get("gls_fr_rest", "get_label", vals)


def test_eu_country():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["country"] = "DE"
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_vat_country_valid():
    """
    Test using incoterm for VAT countries
    From https://gls-group.eu/IE/media/downloads/Customer_information_Brexit~1.pdf
    When exporting with GLS to the UK, dispatchers can choosebetween these Incoterms for
    commercial customs clearance:
    •Incoterm 10 (DDP):
        Freight costs, customs clearance costs, customs duties and taxes paid –
        the sender pays all costsincurred, the importer bears no costs.
    •Incoterm 20 (DAP):
        Freight costs paid, customs clearance costs, customs duties and taxes unpaid –
        the sender pays for freight only, the importer bears all other costs.
    •Incoterm 30 (DDP, VAT unpaid):
        Freight costs, customs clearance costs and customs duties paid, taxes unpaid –
        the sender pays for freight, customs clearance costs and customs duties,
        the importer pays for the taxes incurred.
    •Incoterm 40 (DAP, cleared):
        Freight costs and customs  clearance costs paid, customs duties and taxes unpaid –
        the sender pays for freight and customs clearance costs, the importer pays customs
        duties and taxes.
    •Incoterm 60 (Pick&ShipService, Pick&ReturnService):
        Freight costs, customs clearance costs, customs duties and taxes paid –
        the customer pays all costs incurred, the importer bears no costs.

    In future, we will be able to offer additional, cost-effective inco-terms for customs
    clearance of single parcels to the UK.
    •Incoterm 13 (DDP):
        Freight costs, customs clearance costs, customs duties and taxes paid –
        the sender pays all costs incurred, the importer bears no costs.
    •Incoterm 23 (DAP):
        Freight costs paid, customs clearance costs, customs duties and taxes unpaid –
        the sender paysfor freight only, the importer bears all other costs.
    •Incoterm 43 (DAP, cleared):
        Freight costs and customs clear-ance costs paid, customs duties and taxes unpaid –
        the sender pays for freight and customs clearance costs, the  importer pays customs
        duties and taxes.
    •Incoterm 18 (DDP, VAT pre-registration):
        Freight costs, cus-toms clearance costs and taxes paid –
        the sender pays all costs incurred, the importer bears no costs.
        For single or various parcels with a goods value of less than GBP 135.
        Here, the import VAT can be paid directly to the British tax authorities.

    From GLS-Web-API_FR_V01-03.pdf
    •Incoterm 50:
        Marchandise livrée, dédouanement export & import payés, exemption de faible valeur
        autorisation libre.
    """
    vals = copy.deepcopy(DATA)
    vals["to_address"]["name"] = "Prince"
    vals["to_address"]["street1"] = "Place de Bel-Air"
    vals["to_address"]["zip"] = "1204"
    vals["to_address"]["city"] = "Geneve"
    vals["to_address"]["country"] = "CH"
    vals["service"]["incoterm"] = "20"
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_vat_country_missing_icoterm():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["name"] = "Prince"
    vals["to_address"]["street1"] = "Place de Bel-Air"
    vals["to_address"]["zip"] = "1204"
    vals["to_address"]["city"] = "Geneve"
    vals["to_address"]["country"] = "CH"
    with pytest.raises(CarrierError, match="is missing: Incoterm"):
        result = roulier.get("gls_fr_rest", "get_label", vals)


def test_vat_country_wrong_icoterm():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["name"] = "Prince"
    vals["to_address"]["street1"] = "Place de Bel-Air"
    vals["to_address"]["zip"] = "1204"
    vals["to_address"]["city"] = "Geneve"
    vals["to_address"]["country"] = "CH"
    vals["service"]["incoterm"] = "00"
    with pytest.raises(CarrierError, match="Incoterm is invalid"):
        result = roulier.get("gls_fr_rest", "get_label", vals)


def test_FDS():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_FDS}]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SHD():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["contact"] = "Dylann"
    vals["parcels"][0]["services"] = [
        {"product": SERVICE_SHD, "pickupLocationId": "2500389381"}
    ]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SHD_auto():
    vals = copy.deepcopy(DATA)
    vals["to_address"]["contact"] = "Dylann"
    vals["parcels"][0]["services"] = [{"product": SERVICE_SHD}]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SRS():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_SRS}]
    with pytest.raises(CarrierError, match="is missing: Return Address"):
        roulier.get("gls_fr_rest", "get_label", vals)
    vals["return_address"] = copy.deepcopy(vals["to_address"])
    with pytest.raises(CarrierError, match="is missing: Return parcel weight"):
        roulier.get("gls_fr_rest", "get_label", vals)
    vals["returns"] = [{"weight": 1}]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(vals, result, 1, 0)


def test_SRS_return_only():
    vals = copy.deepcopy(DATA)
    vals["parcels"][0]["services"] = [{"product": SERVICE_SRS}]
    vals["pickup_address"] = copy.deepcopy(vals["to_address"])
    vals["returns"] = [{"weight": 1}]
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(
        vals, result, 1, 0, False
    )  # no label: GLS will generate it inside the agency


def test_PandR():
    vals = copy.deepcopy(DATA)
    vals["pickup_address"] = vals.pop("to_address")
    result = roulier.get("gls_fr_rest", "get_label", vals)
    assert_result(
        vals, result, 1, 0, False
    )  # no label: GLS will generate it inside the agency


def test_PandS():
    vals = copy.deepcopy(DATA)
    vals["pickup_address"] = copy.deepcopy(vals["to_address"])
    result = roulier.get("gls_fr_rest", "get_label", vals)
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
