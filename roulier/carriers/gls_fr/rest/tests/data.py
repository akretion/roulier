from datetime import date
import logging

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
    "service": {
        "shippingDate": date.today(),
        "customerId": credentials["customerId"],
        "agencyId": credentials["agencyId"],
    },
    "parcels": [{"weight": 1.2, "comment": "Fake comment"}],
    "to_address": {
        "name": "Anne O'nyme",
        "street1": "27 rue Léon CAMET",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
        "email": "test@example.com",
    },
}

DATA_FROM_ADDR = {
    "name": "TEST",
    "street1": "72 rue Cécile Honxa",
    "city": "Paris",
    "country": "FR",
    "zip": "75001",
}
