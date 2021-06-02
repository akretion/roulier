from roulier import roulier
from .common import GeodisVcrCommon, insert_real_secrets


class GeodisFrValidateAddressCase(GeodisVcrCommon):
    def test_geodis_correct_address(self):
        payload = {
            "to_address": {
                "city": "COURT SAINT ETIENNE",
                "zip": "1490",
                "country": "BE",
            },
            "auth": {"login": "test login", "password": "pwd", "isTest": True},
        }
        insert_real_secrets(payload)
        ret = roulier.get("geodis_fr", "validate_address", payload)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]["city"], "COURT SAINT ETIENNE")

    def test_geodis_wrong_city(self):
        payload = {
            "to_address": {"city": u"Villeurbanne", "zip": u"59100", "country": u"FR"},
            "auth": {
                "login": u"45393e38323033372b3c3334",
                "password": u"2d5a44584356",
                "isTest": True,
            },
        }
        insert_real_secrets(payload)
        ret = roulier.get("geodis_fr", "validate_address", payload)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]["city"], "ROUBAIX")

    def test_geodis_wrong_zip(self):
        payload = {
            "to_address": {"city": u"ROUBAIX", "zip": u"59199", "country": u"FR"},
            "auth": {
                "login": u"45393e38323033372b3c3334",
                "password": u"2d5a44584356",
                "isTest": True,
            },
        }
        insert_real_secrets(payload)
        ret = roulier.get("geodis_fr", "validate_address", payload)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]["zip"], 59100)
