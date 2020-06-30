# -*- coding: utf-8 -*-
from roulier import roulier
import base64
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
    "parcels": [{"weight": 1.2,}, {"weight": 3.4,},],
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

factory = roulier.factory
carrier_obj = factory.get("laposte_fr", "get_label")

encoder = carrier_obj.encoder(carrier_obj)
decoder = carrier_obj.decoder(carrier_obj)
transport = carrier_obj.transport(carrier_obj)

parcels = data.get("parcels", []).copy()
if carrier_obj.manage_multi_label or len(parcels) == 1:
    payload = encoder.encode(data)
    response = transport.send(payload)
    decoder.decode(response, payload)
else:
    for parcel in parcels:
        data["parcels"] = [parcel]
        payload = encoder.encode(data)
        response = transport.send(payload)
        decoder.decode(response, payload)

# Données envoyées
print("payload.body =", payload.get("body"))

# Résultat
response = decoder.result
if "parcels" in response:
    if len(response["parcels"]) > 0:
        ct = 0
        for parcel in response["parcels"]:
            if "label" in parcel:
                if "data" in parcel["label"]:
                    res = parcel["label"]["data"]
                    print("#### parcel =", ct)
                    print(base64.b64decode(res).decode("utf8"))
                    ct += 1
