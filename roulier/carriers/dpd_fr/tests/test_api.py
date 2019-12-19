from datetime import datetime, date
from roulier import roulier
from ..dpd_encoder import DpdEncoder
from ..dpd_transport import DpdTransport

trans = DpdTransport()
dpd = roulier.get('dpd')

data = {
    'auth': {
        "login": "log",
        "password": "in",

    },
    'from_address': {
        'city': 'Villeurbanne',
        'company': 'Akretion',
        'country': 'France',
        'email': 'raphael.reverdy@akretion.com',
        'name': 'Akretion',
        'phone': '0478787878',
        'street1': '27 rue Henri Rolland',
        'street2': '',
        'zip': '69100'},
 'parcels': [{'weight': '2'}],
 'service': {'agencyId': '1077',
  'customerId': '11715508',
  'dropOffLocation': '',
  'instructions': 'Laisser sur le pas de la porte',
  'labelFormat': 'ZPL',
  'notifications': 'No',
  'product': 'DPD CLASSIC',
  'reference1': 'Facture xyz',
  'reference2': '',
  'reference3': '',
  'shippingDate': date.today().strftime('%Y/%m/%d'),
  'shippingId': '',
  "customerId": "11715508",
  "customerAddressId": "13645482",
  "senderId": "11715508",
  "senderAddressId": "13645487",
  "senderZipCode": "77144",
  "customerCountry": "FR",
  "departureUnitId": "1077",
 },
 'to_address': {'city': 'Lyon',
  'company': 'noiterka',
  'country': 'FR',
  'door1': '1963',
  'door2': '',
  'email': 'contact@akretion.com',
  'firstName': '',
  'intercom': '',
  'name': '',
  'phone': '0770707070',
  'street1': '35 b Rue Montgolfier',
  'street2': '',
  'zip': '69006'}}


def test_encode():
    "Test some fields are encoded correctly"
    encoder = DpdEncoder()
    payload = encoder.encode(data, 'createShipmentWithLabels')
    infos = payload['infos']
    body = payload['body']
    assert infos['action'] == 'createShipmentWithLabels'
    assert body['payerId'] == 11715508 # it should be int
    assert body['receiverFirmName'] == data['to_address']['company']
    assert len(body['parcels']) == len(data['parcels'])
    assert datetime.strptime(body['shipmentDate'], '%Y%M%d')
    assert body['manifest']['fileType'] == 'ZPL'
