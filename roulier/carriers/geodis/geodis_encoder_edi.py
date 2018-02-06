# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from datetime import datetime
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .geodis_api_edi import GeodisApiEdi


class GeodisEncoderEdi(Encoder):

    def api(self):
        api = GeodisApiEdi()
        return api.api_values()

    def encode(self, api_input):
        api = GeodisApiEdi()
        if not api.validate(api_input):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input))
        data = api.normalize(api_input)

        return {
            "body": self.encode_agency(
                agency_address=data['agency_address'],
                from_address=data['from_address'],
                shipments=data['shipments'],
                service=data['service']),
            "headers": data['service'],
        }

    def encode_shipment(self, shipment, service, idx):
        packs = shipment['parcels']
        to_address = shipment['to_address']
        lines = [
            ['CNI', '%s' % idx, shipment['shippingId']],
            ['TSR', '2',  # 4065
                [
                    shipment['product'],
                    '', '',
                    shipment['productOption']  # 7273
                ],
                shipment['productPriority'],  # 4219
                shipment['notifications'],  # 7085 : M, S, P
             ],
            # /*MOA si envoi international */
            # ['MOA', '43', $shipment['cost'], 'EUR'],
            ['FTX', 'DEL', '', '', shipment['reference2']],
            ['TOD', '6', 'PP', shipment['productTOD']],
            ['RFF', ['ADE', service['customerId']]],
            ['RFF', ['ACL', shipment['reference1']]],
            ["NAD", "CN",
                "",
                "",  # C058
                to_address['name'],
                [to_address['street1'], to_address['street2']],
                to_address['city'],
                "",  # 3164
                to_address['zip'],
                to_address['country']
             ],
             ['CTA', 'IC', ['', to_address['name']]], 
        ]
        if to_address['email']:
            lines.append(['COM', [to_address['email'], 'EM']])
        if to_address['phone']:
            lines.append(['COM', [to_address['phone'], 'TE']])
        j = 0
        for pack in packs:
            j = j + 1
            lines += [
                ['GID', '%s' % j, ['1', 'PC', '21', '6']],
                ['MEA', 'AAE', 'AAD', ['KGM', '%s' % pack['weight']]],
                ['PCI', '18'],
                ['GIN', 'BN', pack['barcode']]
            ]
        return lines

    def encode_agency(self, agency_address, from_address, shipments, service):
        shipment_lines = []
        i = 0
        deposit = service['depositId']
        date = datetime.now()
        for shipment in shipments:
            i = i + 1
            shipment_lines += self.encode_shipment(shipment, service, i)

        lines = [
            ['UNH', deposit, ['IFCSUM', 'D', '96A', 'UN', 'ETT021']],
            ['BGM', '630', deposit],
            ['DTM', ['137', date.strftime('%Y%m%d%H%M'), '203']],
            ['RFF', ['ADE', service['customerId']]],
            ['TDT', '20', '', '30', '31'],
            ["NAD", "CA",
                [agency_address['siret'], "100"],
                "",  # C058
                agency_address['name'],
                [agency_address['street1'], agency_address['street2']],
                agency_address['city'],
                "",  # 3164
                agency_address['zip'],
                agency_address['country']
             ],
            ["NAD", "CZ",
                [from_address['siret'], "100"],
                "",  # C058
                from_address['name'],
                [from_address['street1'], from_address['street2']],
                from_address['city'],
                "",  # 3164
                from_address['zip'],
                from_address['country']
             ],
            ['DOC', '630', deposit],
        ] + shipment_lines
        lines += [
            ['UNT', '%s' % (len(lines) + 1), deposit]
        ]
        return lines
