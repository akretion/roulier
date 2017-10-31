# -*- coding: utf-8 -*-
"""Transform input to laposte compatible xml."""
import logging
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .laposte_api import LaposteApi, LAPOSTE_LABEL_FORMAT
LAPOSTE_ACTIONS = ('generateLabelRequest', 'getProductInter')
_logger = logging.getLogger(__name__)


class LaposteEncoder(Encoder):
    """Transform input to laposte compatible xml."""

    def encode(self, api_input, action):
        """Transform input to laposte compatible xml."""
        if not (action in LAPOSTE_ACTIONS):
            raise InvalidApiInput(
                'action %s not in %s' % (action, ', '.join(LAPOSTE_ACTIONS)))

        api = LaposteApi()
        if not api.validate(api_input):
            _logger.warning('Laposte api call exception:')
            raise InvalidApiInput(
                {'api_call_exception': api.errors(api_input)})
        data = api.normalize(api_input)

        data['service']['labelFormat'] = self.lookup_label_format(
            data['service']['labelFormat'])

        env = Environment(
            loader=PackageLoader('roulier', '/carriers/laposte/templates'),
            extensions=['jinja2.ext.with_', 'jinja2.ext.autoescape'],
            autoescape=True)

        template = env.get_template("laposte_%s.xml" % action)
        return {
            "body": template.render(
                service=data['service'],
                parcel=data['parcels'][0],
                auth=data['auth'],
                sender_address=data['from_address'],
                receiver_address=data['to_address'],
                customs=data['customs']),
            "headers": data['auth'],
            "output_format": data['service']['labelFormat']
        }

    def api(self):
        """Return API we are expecting."""
        api = LaposteApi()
        return api.api_values()

    def lookup_label_format(self, label_format="ZPL"):
        """Get a Laposte compatible format of label.

        args:
            label_format: (str) ZPL or ZPL_10x15_300dpi
        return
            a value taken in LAPOSTE_LABEL_FORMAT
        """
        lookup = {
            'ZPL': 'ZPL_10x15_300dpi',
            'DPL': 'DPL_10x15_300dpi',
            'PDF': 'PDF_10x15_300dpi',
        }
        if label_format in LAPOSTE_LABEL_FORMAT:
            return label_format
        return lookup.get(label_format, 'PDF_10x15_300dpi')
