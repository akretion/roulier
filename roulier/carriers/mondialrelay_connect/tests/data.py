"""Sample input and responses for the Mondial Relay Connect tests.

These tests run fully offline (no credentials, no network): the encoder and the
decoder are exercised directly.
"""

DATA = {
    "auth": {
        "login": "BDTEST",
        "password": "PrivateK",
        "isTest": True,
    },
    "service": {
        "customerId": "BDTEST",
        "outputType": "ZplCode",
        "labelFormat": "Generic_ZPL_10x15_203dpi",
        "deliveryMode": "24R",
        "deliveryLocation": "FR-66974",
        "collectionMode": "CCC",
        "orderNo": "CMD123",
        "customerNo": "CLI1",
    },
    "parcels": [
        {
            "weight": 1.2,
            "content": "Colis",
            "reference": "PARCEL-1",
            "length": 30,
            "width": 20,
            "height": 10,
        }
    ],
    "from_address": {
        "name": "Domadoo",
        "street1": "12 avenue du Stade",
        "city": "Perpignan",
        "country": "FR",
        "zip": "66000",
        "email": "logistique@example.com",
    },
    "to_address": {
        "name": "Jean Client",
        "street1": "1 rue de la Paix",
        "street2": "Batiment B",
        "city": "Paris",
        "country": "FR",
        "zip": "75001",
        "email": "jean@example.com",
        "phone": "0102030405",
        "delivery_instruction": "Etage 3, digicode 1234",
    },
}

# Minimal but representative success response (ZPL output + barcode).
RESPONSE_OK = b"""<?xml version="1.0" encoding="utf-8"?>
<ShipmentCreationResponse xmlns="http://www.example.org/Response">
  <StatusList>
    <Status Level="Success" Code="0" Message="Operation successful"/>
  </StatusList>
  <ShipmentsList>
    <Shipment ShipmentNumber="29A00012345">
      <LabelList>
        <Label>
          <Output>^XA^FO50,50^FDMR^FS^XZ</Output>
        </Label>
      </LabelList>
      <ParcelList>
        <Parcel>
          <Barcode Value="29A00012345"/>
        </Parcel>
      </ParcelList>
    </Shipment>
  </ShipmentsList>
</ShipmentCreationResponse>
"""

# Business error response (HTTP 200, error carried as a Status node).
RESPONSE_ERROR = b"""<?xml version="1.0" encoding="utf-8"?>
<ShipmentCreationResponse xmlns="http://www.example.org/Response">
  <StatusList>
    <Status Level="Error" Code="30" Message="Invalid postcode"/>
  </StatusList>
</ShipmentCreationResponse>
"""
