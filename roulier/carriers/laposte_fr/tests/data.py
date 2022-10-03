import logging
from datetime import date

logger = logging.getLogger(__name__)

try:
    from .credential import credentials
except ImportError:
    from .credential_demo import credentials

    logger.debug(
        "To test with real credentials copy and paste "
        "tests/credential_demo.py to tests/credential.py and "
        "fill it with real values"
    )

DATA = {
    "auth": {
        "login": credentials["login"],
        "password": credentials["password"],
        "isTest": credentials["isTest"],
    },
    "service": {"shippingDate": date.today()},
    "parcels": [{"weight": 1.2, "instructions": "Fake instructions"}],
    "to_address": {
        "name": "Fr",
        "firstName": "Hpar",
        "street1": "27 rue Léon CAMET",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
    },
    "from_address": {
        "name": "TEST",
        "firstName": "AUTOMATIC",
        "street1": "72 rue Cécile Honxa",
        "city": "Paris",
        "country": "FR",
        "zip": "75001",
    },
}

PACKING_SLIP_DATA = {
    "auth": {
        "login": credentials["login"],
        "password": credentials["password"],
        "isTest": credentials["isTest"],
    },
}

PARCEL_DOCUMENT_DATA = {
    "auth": {
        "login": credentials["login"],
        "password": credentials["password"],
        "isTest": credentials["isTest"],
    },
    "service": {},
}
