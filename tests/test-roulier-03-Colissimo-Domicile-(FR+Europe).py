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
        "isTest": credentials["isTest"],
    },
    "from_address": {
        "name": "YourCompany",
        "zip": "18540",
        "city": "Scranton",
        "phone": "+15551238069",
        "email": "info@yourcompany.example.com",
        "street1": "1725 Slough Ave.",
        "country": "FR",
        "street": "1725 Slough Ave.",
        "street2": "",
        "street3": "",
        "firstName": ".",
        "company": "YourCompany",
    },
    "to_address": {
        "name": "Roulier Colissimo Domicile (FR + Europe)",
        "zip": "1070",
        "city": "Anderlecht",
        "phone": "+32478719669",
        "mobile": "+32478719669",
        "email": "karl.ajumide@free.com",
        "street2": "immeuble 1",
        "street1": "25 r Caumartin",
        "country": "BE",
        "street": "25 r Caumartin",
        "street3": "",
        "firstName": ".",
        "company": "Roulier Colissimo Domicile (FR + Europe)",
    },
    "service": {
        "product": "DOM",
        "shippingDate": "2020-06-25",
        "labelFormat": None,
        "returnTypeChoice": 3,
        "totalAmount": 13,
    },
    "parcels": [
        {"weight": 3.9000000000000004, "reference": "PACK0000013", "totalAmount": "0"}
    ],
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
