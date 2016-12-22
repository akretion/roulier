# -*- coding: utf-8 -*-
"""Transform input to trs zpl."""
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .trs_api import TrsApi

TRS_ACTIONS = ('generateLabel', 'generateDepositSlip')


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
        api = TrsApi()
        if not api.validate(api_input):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input))
        data = api.normalize(api_input)

        data['to_address']["dept"] = data['to_address']['zip'][0:2]

        return {'body': data, 'header': None}

    def api(self):
        api = TrsApi()
        return api.api_values()
