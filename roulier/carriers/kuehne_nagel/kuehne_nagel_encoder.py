# -*- coding: utf-8 -*-
"""Transform input to kuehne nagel epl."""
from roulier.codec import Encoder


KUEHNE_ACTIONS = ('generateLabel', 'generateDepositSlip')


class KuehneNagelEncoder(Encoder):
    """Transform input to kuehne nagel epl."""

    def encode(self, api_input, action):
        """Dispatcher."""
        if not (action in KUEHNE_ACTIONS):
             raise Exception(
                 'action %s not in %s' % (action, ', '.join(KUEHNE_ACTIONS)))
        api = KuehneNagelApi()
        if not api.validate(api_input):
            _logger.warning('Kuehne Nagel api call exception:')
            raise InvalidApiInput(
                {'api_call_exception': api.errors(api_input)})
        data = api.normalize(api_input)
        if action == 'generateLabel':
            return self.generate_label(data)
        if action == 'generateDepositSlip':
            return self.generate_deposit_slip(data)

    def generate_label(self, data):
#        """Transform input to trs zpl."""
#        dj = self.api()
#        dj['service'].update(api_input.get('service', {}) or {})
#        dj['parcel'].update(api_input.get('parcel', {}) or {})
#        dj['from_address'].update(api_input.get('from_address', {}) or {})
#        dj['to_address'].update(api_input.get('to_address', {}) or {})
#        dj['infos'].update(api_input.get('infos', {}) or {})
#
#        output_format = {}
#        auth = {}
#
#        sender_address = {
#            "companyName": dj['from_address']['companyName'],
#        }
#
#        recipient_address = {
#            "companyName": dj['to_address']['company'],
#            "contact": dj['to_address']['contact'],
#            "name": dj['to_address']['name'],
#            "street1": dj['to_address']['street1'],
#            "street2": dj['to_address']['street2'],
#            "city": dj['to_address']['city'],
#            "zipCode": dj['to_address']['zip'],
#            "phoneNumber": dj['to_address']['phone'],
#            "dept": dj['to_address']['zip'][0:2],
#            "email": dj['to_address']['email'],
#            "phone": dj['to_address']['phone'],
#        }
#        return {
#            'sender_address': sender_address,
#            'recipient_address': recipient_address,
#            'parcel': dj['parcel'],
#            'service': dj['service'],
#            'output_format': output_format,
#            'auth': auth,
#        }
        return {
            'service': data['service'],
            'parcel': data['parcel'],
            'auth': data['auth'],
            'sender_address': data['from_address'],
            'receiver_address': data['to_address'],
        }

    def generate_deposit_slip(self, data):
        """Transform input to trs zpl."""
#        print 'input', api_input
#        dj = {
#            'service': api_input.get('service', {}),
#            'from_address': api_input.get('from_address', {}),
#            'to_address': api_input.get('to_address', {})
#        }
#        if not dj['service']['deliveryContract']:
#            dj['service']['deliveryContract'] = ''
#        output_format = {}
#        auth = {}
#
#        sender_address = {
#            "number": dj['from_address']['number'],
#            "siret": dj['from_address']['siret'],
#            "name": dj['from_address']['name'],
#        }
#
#        recipient_address = {
#            "number": dj['to_address']['number'],
#            "siret": dj['to_address']['siret'],
#            "name": dj['to_address']['name'],
#        }
        result = {
            'service': data['service'],
            'parcel': data['parcel'],
            'auth': data['auth'],
            'sender_address': data['from_address'],
            'receiver_address': data['to_address'],
        }
        result.update({'lines': data.get('lines', [])})
        print 'resul', result
        return result
