from roulier import roulier
import datetime


PAYLOAD = {
    "auth": {"login": "Demo Account", "password": "Demo password", "isTest": True},
    "from_address": {
        "name": "My Test Company",
        "zip": "69100",
        "city": "VILLEURBANNE",
        "phone": "+33475457854",
        "email": "info@yourcompany.com",
        "street1": "250 rue du test",
        "country": "FR",
        "company": "My Test Company/FR/69100/VILLEURBANNE",
    },
    "to_address": {
        "name": "Test 1",
        "zip": "81170",
        "city": "BOURNAZEL",
        "street1": "39 rue du test",
        "country": "FR",
        "phone": "",
    },
    "service": {
        "product": False,
        "shippingDate": datetime.datetime(2023, 6, 14, 9, 49, 39),
        "labelFormat": None,
        "customerId": "1234",
        "goodsName": "Furniture",
        "shippingOffice": "31",
        "shippingRound": "RI81",
        "exportHub": "FR-LBI1",
        "shippingName": "WHOUT00044",
        "deliveryContract": "",
        "labelDeliveryContract": "C",
        "orderName": "S00058",
        "shippingConfig": False,
        "vatConfig": False,
        "deliveryType": "R",
        "note": "",
        "labelLogo": False,
        "kuehneOfficeName": "KUEHNE NAGEL ROAD / AG : FR 62 HARNES",
    },
    "parcels": [{"weight": 0.01, "reference": "PACK0000028"}],
}


def test_kuehne_nagel_fr_get_label_one_pack():
    ret = roulier.get("kuehne_nagel_fr", "get_label", PAYLOAD)
    parcels = ret.get("parcels")
    assert (len(parcels), 1)
    parcel = parcels[0]
    assert (parcel.get("reference"), "PACK0000028")
    assert (bool(parcel["label"].get("data")), True)
