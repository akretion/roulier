"""Transform to/from a carrier specific format."""
from .tools import get_subclass
from .exception import InvalidApiInput
from .api import Api
import logging

_logger = logging.getLogger(__name__)


class Encoder(object):
    _carrier_type = ''
    _action = []

    @classmethod
    def _get_actions_mapping(cls):
        return {}

    @classmethod
    def get_technical_action(cls, action):
        mapping = cls._get_actions_mapping()
        technical_action = mapping.get(action, '')
        return technical_action

    def _extra_input_data_processing(self, input_payload, data):
        return data

    def transform_input_to_carrier_webservice(self, data, action):
        NotImplementedError("Subclass should implement this")

    def encode(self, input_payload, action):
        """Transform input from external app to compatible input for carrier webservice."""
        technical_action = self.get_technical_action(action)
        if not technical_action:
            raise
        validator = get_subclass(Api, self._carrier_type, action)()
        if not validator.validate(input_payload):
            _logger.warning('Laposte api call exception:')
            raise InvalidApiInput(
                {'api_call_exception': validator.errors(input_payload)})
        data = validator.normalize(input_payload)

        data = self._extra_input_data_processing(input_payload, data)

        return self.transform_input_to_carrier_webservice(data, technical_action)


class Decoder(object):
    _carrier_type = ''
    _action = []
    pass

