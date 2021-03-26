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
    "service": {
        "shippingDate": date.today(),
        "customerId": credentials["customerId"],
        "customerCountry": credentials["customerCountry"],
        "agencyId": credentials["agencyId"],
        "product": "DPD_Classic",
        "labelFormat": "PDF",
    },
    "parcels": [{"weight": 1.2, "comment": "Fake comment"}],
    "from_address": {
        "name": "Fr",
        "street1": "27 rue Léon CAMET",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
        "phone": "+330123456789",
    },
    "to_address": {
        "name": "Fr",
        "firstName": "Hpar",
        "street1": "27 rue Léon CAMET",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
        "email": "test@example.com",
    },
}

MY_IP_IS_ALLOWED = credentials.get("my_IP_is_allowed", False)
