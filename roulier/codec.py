"""Transform to/from a carrier specific format."""
from abc import ABC, abstractmethod
from .exception import InvalidApiInput
from .api import ApiParcel
import logging

_logger = logging.getLogger(__name__)


class Encoder(ABC):

    def __init__(self, config_object):
        self.config = config_object

    def _extra_input_data_processing(self, input_payload, data):
        return data

    @abstractmethod
    def transform_input_to_carrier_webservice(self, data, action):
        pass

    def encode(self, input_payload):
        """Transform input from external app to compatible input for carrier webservice."""
        validator = self.config.api(self.config)
        if not validator.validate(input_payload):
            _logger.warning('Laposte api call exception:')
            raise InvalidApiInput(
                {'api_call_exception': validator.errors(input_payload)})
        data = validator.normalize(input_payload)
        data = self._extra_input_data_processing(input_payload, data)
        return self.transform_input_to_carrier_webservice(data)


class Decoder(ABC):

    def __init__(self, config_object):
        self.config = config_object

    @abstractmethod
    def decode(self, answer):
        """Transform a specific representation to python dict.
        Args:
            answer: specific representation of an response of the carrier
        Return:
            Python dict
        """
        return
