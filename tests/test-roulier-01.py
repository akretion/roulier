# -*- coding: utf-8 -*-
from roulier import roulier
import logging

logger = logging.getLogger(__name__)

try:
    from credential import credentials
except ImportError:
    logger.debug(
        "To test with real credentials copy and paste "
        "tests/credential_demo.py to tests/credential.py and "
        "fill it with real values"
    )

data = {
    "auth": {
        "login": credentials["login"],
        "password": credentials["password"],
        "isTest'": credentials["isTest"],
    },
    "service": {"product": "COL", "productCode": "COL", "shippingDate": "2020-06-30",},
    "parcels": [{"weight": 1.2,},],
    "to_address": {
        "name": "Hparfr",
        "firstName": "Hparfr",
        "street1": "35 b Rue Montgolfier",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
    },
    "from_address": {
        "name": "Hparfr",
        "fristName": "Akretion France",
        "street1": "35 b Rue Montgolfier",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
    },
}

print(roulier.get_carriers_action_available())
print(roulier.get("laposte_fr", "get_label", data))
