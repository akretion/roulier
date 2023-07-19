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
            "to_address": {"city": "Villeurbanne", "zip": "59100", "country": "FR"},
            "auth": {
                "login": "45393e38323033372b3c3334",
                "password": "2d5a44584356",
                "isTest": True,
            },
        }
        insert_real_secrets(payload)
        ret = roulier.get("geodis_fr", "validate_address", payload)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]["city"], "ROUBAIX")

    def test_geodis_wrong_zip(self):
        payload = {
            "to_address": {"city": "ROUBAIX", "zip": "59199", "country": "FR"},
            "auth": {
                "login": "45393e38323033372b3c3334",
                "password": "2d5a44584356",
                "isTest": True,
            },
        }
        insert_real_secrets(payload)
        ret = roulier.get("geodis_fr", "validate_address", payload)
        self.assertEqual(len(ret), 1)
        self.assertEqual(ret[0]["zip"], 59100)
