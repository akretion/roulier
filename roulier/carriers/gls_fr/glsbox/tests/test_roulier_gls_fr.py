from datetime import date
import logging

from roulier import roulier

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


def test_connexion():
    roulier.get(
        "gls_fr_glsbox",
        "get_label",
        {
            "auth": {"login": credentials["login"], "isTest": credentials["isTest"]},
            "service": {
                "agencyId": credentials["agencyId"],
                "customerId": credentials["customerId"],
                "shippingDate": date.today(),
                "shippingId": "125874",
                "intructions": "Sent from automatic test",
                "parcel_total_number": 1,
            },
            "from_address": {
                "company": "my company",
                "name": "my name",
                "street1": "blablabla street",
                "zip": "69000",
                "city": "Lyon",
                "phone": "04 99 99 99 99",
                "email": "contact@mycompany.fr",
            },
            "to_address": {
                "company": "my customer",
                "name": "Martine MARTIN",
                "street1": "13 avenue des champs Elysées",
                "zip": "75001",
                "city": "Paris",
                "phone": "01 99 99 99 99",
                "email": "contact@mycustomer.fr",
                "country": "FR",
            },
            "parcels": [
                {
                    "weight": 3.4,
                    "parcel_number_label": 1,
                    "parcel_number_barcode": 1,
                    "custom_sequence": "1234567899",
                }
            ],
        },
    )
