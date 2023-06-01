from roulier import roulier
import datetime


PAYLOAD = {
    "sender_info": {
        "number": 792377731,
        "siret": "79237773100023",
        "name": "My Test Company",
    },
    "recipient_info": {
        "number": "493191407",
        "siret": "49319140700458",
        "name": "HARNES",
    },
    "auth": {"login": "Demo Account", "password": "Demo password", "isTest": True},
    "shipments": [
        {
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
                "shippingDate": datetime.datetime(2023, 6, 14, 9, 58, 50),
                "labelFormat": None,
                "customerId": "1234",
                "goodsName": "Furniture",
                "shippingOffice": "31",
                "shippingRound": "RI81",
                "exportHub": "FR-LBI1",
                "shippingName": "WHOUT00045",
                "deliveryContract": "",
                "labelDeliveryContract": "C",
                "orderName": "S00060",
                "shippingConfig": False,
                "vatConfig": False,
                "deliveryType": "R",
                "note": "",
                "labelLogo": False,
                "kuehneOfficeName": "KUEHNE NAGEL ROAD / AG : FR 62 HARNES",
            },
            "parcels": [{"weight": 0.01, "reference": "PACK0000029"}],
        },
        {
            "to_address": {
                "name": "Test 2",
                "zip": "81200",
                "city": "AUSSILLON",
                "street1": "40 rue du test",
                "country": "FR",
                "phone": "",
            },
            "service": {
                "product": False,
                "shippingDate": datetime.datetime(2023, 6, 14, 9, 58, 50),
                "labelFormat": None,
                "customerId": "1234",
                "goodsName": "Furniture",
                "shippingOffice": "12",
                "shippingRound": "MS81",
                "exportHub": "FR-DCM",
                "shippingName": "WHOUT00046",
                "deliveryContract": "",
                "labelDeliveryContract": "C",
                "orderName": "S00061",
                "shippingConfig": False,
                "vatConfig": False,
                "deliveryType": "R",
                "note": "",
                "labelLogo": False,
                "kuehneOfficeName": "KUEHNE NAGEL ROAD / AG : FR 62 HARNES",
            },
            "parcels": [{"weight": 0.01, "reference": "PACK0000030"}],
        },
    ],
    "service": {
        "date": "230614",
        "hour": "0958",
        "depositNumber": "7",
        "deliveryContract": "",
        "shippingConfig": "",
        "vatConfig": "",
        "invoicingContract": "Demo Account",
        "goodsName": "Furniture",
    },
}


def test_kuehne_nagel_fr_get_edi():
    ret = roulier.get("kuehne_nagel_fr", "get_edi", PAYLOAD)
    assert (bool(ret), True)
    assert (type(ret), str)
    test_line = "UNB+UNOC:1+792377731:22+493191407:22+230614:0958+7'"
    lines = ret.split("\n")
    assert (lines[1], test_line)
