# -*- coding: utf-8 -*-
"""Transform input to kuehne nagel epl."""
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .kuehne_nagel_api import KuehneNagelApi, KuehneNagelDepositApi
import logging

_logger = logging.getLogger(__name__)

KUEHNE_ACTIONS = ('generateLabel', 'generateDepositSlip')


class KuehneNagelEncoder(Encoder):
    """Transform input to kuehne nagel epl."""

    def encode(self, api_input, action):
        """Dispatcher."""
        if not (action in KUEHNE_ACTIONS):
             raise Exception(
                 'action %s not in %s' % (action, ', '.join(KUEHNE_ACTIONS)))
        if action == 'generateLabel':
            api = KuehneNagelApi()
        if action == 'generateDepositSlip':
            api = KuehneNagelDepositApi()
        if not api.validate(api_input):
            _logger.warning('Kuehne Nagel api call exception:')
            raise InvalidApiInput(
                {'api_call_exception': api.errors(api_input)})
        data = api.normalize(api_input)
        return data

    def api(self):
        """Return API we are expecting."""
        api = KuehneNagelApi()
        return api.api_values()
