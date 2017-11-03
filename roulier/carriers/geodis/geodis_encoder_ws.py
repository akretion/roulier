# -*- coding: utf-8 -*-
"""Transform input to geodis compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .geodis_api_ws import GeodisApiWs

GEODIS_ACTIONS = ('demandeImpressionEtiquette',)


class GeodisEncoderWs(Encoder):
    """Transform input to geodis compatible xml."""

    def encode(self, api_input, action):
        """Transform input to geodis compatible xml."""
        if not (action in GEODIS_ACTIONS):
            raise InvalidApiInput(
                'action %s not in %s' % (action, ', '.join(GEODIS_ACTIONS)))

        api = GeodisApiWs()
        if not api.validate(api_input):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input))
        data = api.normalize(api_input)

        data['service']['labelFormat'] = self.lookup_label_format(
            data['service']['labelFormat'])
        data['service']['shippingDate'] = data['service']['shippingDate'].replace('/','') 
        data['from_address']['departement'] = data['from_address']['zip'][:2]

        is_test = data['service']['is_test']

        env = Environment(
            loader=PackageLoader('roulier', '/carriers/geodis/templates'),
            extensions=['jinja2.ext.with_', 'jinja2.ext.autoescape'],
            autoescape=True)

        template = env.get_template("geodis_%s.xml" % action)
        return {
            "body": template.render(
                service=data['service'],
                parcels=data['parcels'],
                sender_address=data['from_address'],
                receiver_address=data['to_address']),
            "headers": data['auth'],
            "is_test": is_test,
            "output_format": api_input['service']['labelFormat']
        }

    def api(self):
        api = GeodisApiWs()
        return api.api_values()

    def lookup_label_format(self, label_format="ZPL"):
        """Get a Geodis compatible format of label.

        args:
            label_format: (str) ZPL or PDF
        return
            a value taken in GEODIS_LABEL_FORMAT
        """
        lookup = {
            'ZPL': 'Z',
            'PDF': 'P',
            'HTML': 'H',
            'XML': 'X',
            'EPL2': 'E',
            'Z': 'Z',
            'P': 'P',
            'H': 'H',
            'X': 'X',
            'E': 'E',
        }
        return lookup.get(label_format.upper(), 'Z')
