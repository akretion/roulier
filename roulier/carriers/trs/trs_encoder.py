# -*- coding: utf-8 -*-
"""Transform input to trs zpl."""
from roulier.codec import Encoder

TRS_ACTIONS = ('generateLabel', 'generateDeliverySlip')


class TrsEncoder(Encoder):
    """Transform input to trs zpl."""

    def encode(self, api_input, action):
        """Dispatcher."""
        if action == 'generateLabel':
            return self.generate_label(api_input)
        raise Exception(
            'action %s not in %s' % (action, ', '.join(TRS_ACTIONS)))

    def generate_label(self, api_input):
        """Transform input to trs zpl."""
        dj = self.api()
        dj['service'].update(api_input.get('service', {}) or {})
        dj['parcel'].update(api_input.get('parcel', {}) or {})
        dj['from_address'].update(api_input.get('from_address', {}) or {})
        dj['to_address'].update(api_input.get('to_address', {}) or {})
        dj['infos'].update(api_input.get('infos', {}) or {})

        service = {
            'shippingReference': dj['service']['shippingReference'],
            'shippingDate': dj['service']['shippingDate'],
        }
        output_format = {}
        auth = {}

        parcel = {
            "reference": dj['parcel']['reference'],
            "weight": dj['parcel']['weight'],
            "barcode": dj['parcel']['barcode'],
        }

        sender_address = {
            "companyName": dj['from_address']['company'],
        }

        receiver_address = {
            "companyName": dj['to_address']['company'],
            "name": dj['to_address']['name'],
            "street1": dj['to_address']['street1'],
            "street2": dj['to_address']['street2'],
            "city": dj['to_address']['city'],
            "zipCode": dj['to_address']['zip'],
            "phoneNumber": dj['to_address']['phone'],
            "dept": dj['to_address']['zip'][0:2],
            "email": dj['to_address']['email'],
        }
        return {
            'sender_address': sender_address,
            'receiver_address': receiver_address,
            'parcel': parcel,
            'service': service,
            'output_format': output_format,
            'auth': auth,
        }

    def api(self):
        """Return API we are expecting."""
        address = {
            'company': "",
            'name': "",
            'street1': "",
            'street2': "",
            'country': "",
            'city': "",
            'zip': "",
            'phone': "",
            'email': "",
            "intercom": "",
        }

        return {
            "service": {
                'productCode': '',
                'shippingDate': '',
                'labelFormat': '',
                'shippingReference': '',
            },
            "parcel": {
                "reference": "",
            },
            "to_address": address.copy(),
            "from_address": address.copy(),
            "infos": {
                'contractNumber': '',
                'password': ''
            }
        }
