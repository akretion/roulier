# -*- coding: utf-8 -*-
"""Transform input to dummy zpl."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder

DUMMY_ACTIONS = ('generateLabel')


class DummyEncoder(Encoder):
    """Transform input to dummy zpl."""

    def encode(self, api_input, action):
        """Transform input to dummy zpl."""
        if not (action in DUMMY_ACTIONS):
            raise Exception(
                'action %s not in %s' % (action, ', '.join(DUMMY_ACTIONS)))

        dj = self.api()
        dj['service'].update(api_input.get('service', {}) or {})
        dj['parcel'].update(api_input.get('parcel', {}) or {})
        dj['from_address'].update(api_input.get('from_address', {}) or {})
        dj['to_address'].update(api_input.get('to_address', {}) or {})
        dj['infos'].update(api_input.get('infos', {}) or {})

        service = {
            'shippingReference': dj['service']['shippingReference']
        }
        output_format = {}
        auth = {}

        parcel = {
            "reference": dj['parcel']['reference'],
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
            "dept": dj['to_address']['zip'][0:2]
        }

        env = Environment(
            loader=PackageLoader('roulier', '/carriers/dummy/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("dummy_%s.zpl" % action)
        return template.render(
            auth=auth,
            service=service,
            outputFormat=output_format,
            parcel=parcel,
            sender_address=sender_address,
            receiver_address=receiver_address)

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
