# Mondial Relay Connect (`mondialrelay_connect`)

Implementation of the Mondial Relay **Connect** REST API (Web Service Dual
Carrier) for label creation.

This is distinct from the existing `mondialrelay` carrier, which targets the
older SOAP/WSI web service. The Connect API uses a different endpoint and an XML
request/response over HTTPS:

- Production: `https://connect-api.mondialrelay.com/api/shipment`
- Sandbox: `https://connect-api-sandbox.mondialrelay.com/api/shipment`

Authentication (`Login` / `Password` / `CustomerId`) is carried inside the XML
`<Context>`, not via HTTP headers. Set `auth.isTest` to use the sandbox URL.

## Action

- `get_label`

## Example

```python
from datetime import date
from roulier import roulier

result = roulier.get(
    "mondialrelay_connect",
    "get_label",
    {
        "auth": {"login": "BDTEST", "password": "PrivateK", "isTest": True},
        "service": {
            "customerId": "BDTEST",
            "outputType": "ZplCode",
            "labelFormat": "Generic_ZPL_10x15_203dpi",
            "deliveryMode": "24R",
            "deliveryLocation": "FR-66974",
            "orderNo": "CMD123",
        },
        "parcels": [{"weight": 1.2, "content": "Colis"}],
        "from_address": {
            "name": "My Company",
            "street1": "12 avenue du Stade",
            "city": "Perpignan",
            "country": "FR",
            "zip": "66000",
        },
        "to_address": {
            "name": "Jean Client",
            "street1": "1 rue de la Paix",
            "city": "Paris",
            "country": "FR",
            "zip": "75001",
            "delivery_instruction": "Etage 3",
        },
    },
)
```

## Input notes

- `service.outputType`: `PdfUrl` (default), `ZplCode` or `IplCode`.
- `service.labelFormat`: output format (e.g. `10x15`, `A4`,
  `Generic_ZPL_10x15_203dpi`).
- `service.deliveryMode` / `deliveryLocation`: routing, e.g. `24R` +
  `FR-66974` for a pickup point.
- `parcel.weight` is in kilograms (converted to grams, 10 g floor).
- `parcel.length` / `width` / `height` are optional, in centimeters.
- `to_address.delivery_instruction` maps to `DeliveryInstruction`.
- Address extras: `title`, `firstname`, `lastname`, `houseNo`, `mobile`.

## Output

Standard roulier `get_label` output. The Connect API returns a single label
stream for the shipment; it is attached to the first parcel, and each returned
barcode yields a parcel entry with its tracking number.

## Tests

The tests run fully offline (no credentials, no network): they exercise the
encoder (XML structure) and the decoder (sample responses) directly.

```sh
pytest roulier/carriers/mondialrelay_connect/tests/
```
