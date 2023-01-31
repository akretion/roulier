from roulier import roulier
import datetime
from .common import insert_real_secrets


PAYLOAD = {
    "shipments": [
        {
            "product": u"MES",
            "productOption": "RDW",
            "to_address": {
                "city": u"PARIS",
                "name": u"Test Customer",
                "zip": u"75015",
                "street1": u"12 RUE DE LA CONVENTION",
                "street2": "",
                "street3": "",
                "phone": u"+33778787878",
                "country": u"FR",
                "email": u"test@test.com",
            },
            "productPriority": "3",
            "notifications": "P",
            "productTOD": "P",
            "reference2": "",
            "reference1": u"test-ref",
            "shippingId": u"11111111",
            "reference3": "",
            "parcels": [
                {"barcode": u"JVGTC1111111111111111", "weight": 5.0},
                {"barcode": u"JVGTC1234567891111111", "weight": 4.0},
            ],
        }
    ],
    "from_address": {
        "city": u"VILLEURBANNE",
        "name": u"AKRETION",
        "zip": u"69100",
        "street1": u"27 rue Henri Rolland",
        "street2": "",
        "street3": "",
        "phone": u"+33645452556",
        "country": u"FR",
        "siret": u"79237773100023",
        "email": u"contact@test.com",
    },
    "service": {
        "depositId": "11111",
        "interchangeSender": u"987654321",
        "interchangeRecipient": u"123456789",
        "depositDate": datetime.datetime(2020, 12, 21, 13, 14, 53),
        "customerId": u"193032",
    },
    "sender_id": 1,
    "agency_id": u"021059",
    "agency_address": {
        "city": u"Lomme",
        "name": u"Geodis Lille Europe",
        "zip": u"59160",
        "mobile": u"+33320085555",
        "street1": u"7 Avenue de la Rotonde",
        "street2": "",
        "street3": "",
        "phone": u"+33320085555",
        "country": u"FR",
        "siret": u"45750735800044",
    },
}


def test_geodis_generate_edi_file():
    insert_real_secrets(PAYLOAD)
    ret = roulier.get("geodis_fr", "get_edi", PAYLOAD)
    # We should make some check about the content
    assert ret
