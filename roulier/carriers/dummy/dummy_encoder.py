# -*- coding: utf-8 -*-
"""Transform input to dummy zpl."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .dummy_api import DummyApi

DUMMY_ACTIONS = ('generateLabel')


class DummyEncoder(Encoder):
    """Transform input to dummy zpl."""

    def encode(self, api_input, action):
        """Transform input to dummy zpl."""
        if not (action in DUMMY_ACTIONS):
            raise Exception(
                'action %s not in %s' % (action, ', '.join(DUMMY_ACTIONS)))

        api = DummyApi()
        if not api.validate(api_input):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input))
        data = api.normalize(api_input)

        data['to_address']['dept'] = data['to_address']['zip'][0:2]

        env = Environment(
            loader=PackageLoader('roulier', '/carriers/dummy/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("dummy_%s.zpl" % action)
        return template.render(
            auth=data['auth'],
            service=data['service'],
            parcel=data['parcel'],
            sender_address=data['from_address'],
            receiver_address=data['to_address'])

    def api(self):
        """Return API we are expecting."""
        api = DummyApi()
        return api.api_values()
