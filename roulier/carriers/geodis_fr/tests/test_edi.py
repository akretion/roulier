from roulier import roulier
import datetime
from .common import insert_real_secrets


PAYLOAD = {
    "shipments": [
        {
            "product": "MES",
            "productOption": "RDW",
            "to_address": {
                "city": "PARIS",
                "name": "Test Customer",
                "zip": "75015",
                "street1": "12 RUE DE LA CONVENTION",
                "street2": "",
                "street3": "",
                "phone": "+33778787878",
                "country": "FR",
                "email": "test@test.com",
            },
            "productPriority": "3",
            "notifications": "P",
            "productTOD": "P",
            "reference2": "",
            "reference1": "test-ref",
            "shippingId": "11111111",
            "reference3": "",
            "parcels": [
                {"barcode": "JVGTC1111111111111111", "weight": 5.0},
                {"barcode": "JVGTC1234567891111111", "weight": 4.0},
            ],
        }
    ],
    "from_address": {
        "city": "VILLEURBANNE",
        "name": "AKRETION",
        "zip": "69100",
        "street1": "27 rue Henri Rolland",
        "street2": "",
        "street3": "",
        "phone": "+33645452556",
        "country": "FR",
        "siret": "79237773100023",
        "email": "contact@test.com",
    },
    "service": {
        "depositId": "11111",
        "interchangeSender": "987654321",
        "interchangeRecipient": "123456789",
        "depositDate": datetime.datetime(2020, 12, 21, 13, 14, 53),
        "customerId": "193032",
    },
    "sender_id": 1,
    "agency_id": "021059",
    "agency_address": {
        "city": "Lomme",
        "name": "Geodis Lille Europe",
        "zip": "59160",
        "mobile": "+33320085555",
        "street1": "7 Avenue de la Rotonde",
        "street2": "",
        "street3": "",
        "phone": "+33320085555",
        "country": "FR",
        "siret": "45750735800044",
    },
}


def test_geodis_generate_edi_file():
    insert_real_secrets(PAYLOAD)
    ret = roulier.get("geodis_fr", "get_edi", PAYLOAD)
    # We should make some check about the content
    assert ret
