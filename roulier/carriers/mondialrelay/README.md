Mondial Relay get_label example:

```python

from roulier import roulier

payload = {
    "auth": {
        "login": "BDTEST13",
        "password": "PrivateK",
    },
    "service": {
        "product": "LCC",
        "pickupMode": "REL",
        "pickupSite": "AUTO",
        "pickupCountry": "FR",
    },
    "parcels": [
        {
            "weight": 3.4,
        }
    ],
    "to_address": {
        "name": "Hparfr",
        "street1": "35 b Rue Montgolfier",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
        "phone": "+33612121212",
        "lang": "FR",
    },
    "from_address": {
        "name": "Akretion France",
        "street1": "35 b Rue Montgolfier",
        "city": "Villeurbanne",
        "country": "FR",
        "zip": "69100",
        "phone": "+33612121212",
        "lang": "FR",
    },
}

response = roulier.get("mondialrelay", "get_label", payload)

print(response)
```
