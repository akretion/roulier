import logging
import copy
import base64
import requests
import shutil
import pytest
import os
import time

from roulier import roulier
from roulier.exception import InvalidApiInput, CarrierError

from .data import DATA, PARCEL_DOCUMENT_DATA
from .test_laposte_basic import test_methods

logger = logging.getLogger(__name__)

DOWNLOAD_PDF_FILE = False  # Update to get demo files

EXCEPTION_MESSAGE = "Failed call with parameters %s"

fake_parcels = []


def _get_fake_parcel(new_one=False, sleep=False):
    if not new_one and fake_parcels:
        return fake_parcels[0]
    vals = copy.deepcopy(DATA)
    vals["service"]["product"] = "COM"
    vals["service"]["transportationAmount"] = 123
    vals["service"]["totalAmount"] = 123
    vals["to_address"]["country"] = "GP"  # Guadeloupe
    vals["to_address"]["zip"] = "97100"  # Basse-Terre
    vals["parcels"][0]["customs"] = {
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
    vals["parcels"][0]["totalAmount"] = 123  # Frais de transport
    result = roulier.get("laposte_fr", "get_label", vals)
    parcel = result["parcels"][0]
    parcel["tracking"]["partner"] = "0097100118Q5380511833101312A"
    parcel["tracking"]["number"] = "8Q53804957971"
    vals = copy.deepcopy(PARCEL_DOCUMENT_DATA)
    vals["service"]["parcel_number"] = parcel["tracking"]["partner"]
    while True:
        try:
            result = roulier.get("laposte_fr", "get_documents", vals)
        except CarrierError as e:
            if e.response.status_code != 404 or i > 300:
                raise
            i += 30
            time.sleep(30)
        else:
            break
    parcel["documents"] = result
    fake_parcels.append(parcel)
    return fake_parcels[-1]


def test_get_documents_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PARCEL_DOCUMENT_DATA)
    with pytest.raises(InvalidApiInput, match="parcel_number"):
        roulier.get("laposte_fr", "get_documents", vals)
    fake_parcel = _get_fake_parcel()
    vals["service"]["parcel_number"] = fake_parcel["tracking"]["partner"]
    documents = roulier.get("laposte_fr", "get_documents", vals)
    assert documents and isinstance(documents, dict)
    doc_types = set()
    for doc in documents.values():
        doc_types.add(doc["documentType"])
    assert "CN23" in doc_types


def test_get_document_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PARCEL_DOCUMENT_DATA)
    fake_parcel = _get_fake_parcel()
    vals["service"]["parcel_number"] = fake_parcel["tracking"]["partner"]
    docs = list(fake_parcel["documents"].values())
    vals["service"]["document_id"] = docs[0]["path"]
    resp = roulier.get("laposte_fr", "get_document", vals)
    assert resp and "file" in resp
    assert resp["file"][0:4] == b"%PDF"


def test_create_document_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PARCEL_DOCUMENT_DATA)
    fake_parcel = _get_fake_parcel()
    vals["service"] = {
        "parcel_number": fake_parcel["tracking"]["number"],
        "document_type": "COMMERCIAL_INVOICE",
        "document_path": _get_invoice(),
        "account_number": PARCEL_DOCUMENT_DATA["auth"]["login"],
    }
    doc_uuid = roulier.get("laposte_fr", "create_document", vals)
    assert doc_uuid


def test_update_document_basic_checks():
    if _do_not_execute_test_on_remote():
        return
    vals = copy.deepcopy(PARCEL_DOCUMENT_DATA)
    fake_parcel = _get_fake_parcel()
    vals["service"] = {
        "parcel_number": fake_parcel["tracking"]["number"],
        "document_type": "COMMERCIAL_INVOICE",
        "document_path": _get_invoice(),
        "account_number": PARCEL_DOCUMENT_DATA["auth"]["login"],
    }
    doc_uuid = roulier.get("laposte_fr", "create_document", vals)
    assert doc_uuid


def _get_invoice():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    invoice_path = dir_path + "/test-facture.pdf"
    return invoice_path
    # with open(invoice_path, mode='rb') as file:
    #     fileContent = file.read()
    # return fileContent


def _do_not_execute_test_on_remote():
    """Test execution require valid credentials
    which are not included in commited files.

    Main tests are only executable in local installation.
    This method when called allow to escape remote tests
    """
    if DATA["auth"]["password"] == "blablabla":
        return True
    return False
