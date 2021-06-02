from roulier import roulier
import datetime
from .common import GeodisVcrCommon, insert_real_secrets


PAYLOAD = {
    "auth": {
        "login": "account_test_number",
        "password": "123456789101",
        "isTest": True,
    },
    "from_address": {
        "name": "Akretion",
        "zip": "69100",
        "city": "VILLEURBANNE",
        "phone": "+33645454545",
        "email": "info@test.com",
        "street1": "27 Rue Henri Rolland",
        "country": "FR",
        "street2": "",
        "street3": "",
    },
    "to_address": {
        "name": "Jean Dupont",
        "zip": "69100",
        "city": "VILLEURBANNE",
        "mobile": "+33674747474",
        "email": "jean.dupont@test.com",
        "street1": "40 rue du test",
        "country": "FR",
        "phone": "+33674747474",
        "street2": "",
        "street3": "",
    },
    "service": {
        "product": "MES",
        "shippingDate": datetime.date.today(),
        "labelFormat": "ZPL",
        "option": "",
        "notifications": None,
        "customerId": "123456",
        "agencyId": "021059",
        "hubId": "059",
        "shippingId": "00000001",
    },
    "parcels": [{"weight": 0.03, "reference": "PACK0000045"}],
}


class GeodisGetLabelCase(GeodisVcrCommon):
    def test_geodis_get_label_one_pack(self):
        insert_real_secrets(PAYLOAD)
        ret = roulier.get("geodis_fr", "get_label", PAYLOAD)
        parcels = ret.get("parcels")
        self.assertEqual(len(parcels), 1)
        parcel = parcels[0]
        self.assertEqual(parcel.get("reference"), "PACK0000045")
        self.assertTrue(parcel["label"].get("data"))
