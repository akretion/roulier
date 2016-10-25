# -*- coding: utf-8 -*-
"""Implement for kuehne nagel."""
from roulier.transport import Transport
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
from io import BytesIO

import logging

log = logging.getLogger(__name__)


class KuehneNagelTransport(Transport):
    """Generate EPL offline and txt for EDI."""

    STATUS_SUCCESS = "Success"

    def send(self, body):
        """Call this function.
        Args:
            body: an object with a lot usefull values
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (None)
                response: (None)
                payload: usefull payload (if success) (body as string)
            }
        """
        conv_body = self.convert_dict(body.copy())
        payload = {
            'epl': self.generate_epl(body),
            'line': self.generate_deposit_line(conv_body),
            'parcel': self.generate_parcel_line(conv_body),
            'footer': self.generate_footer_line(conv_body)
        }
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": payload,
        }

    def convert_string(self, string):
        converted_string = string
        if isinstance(string, str):
            converted_string = string.replace('?', '??').replace("'", "?'").replace('+', '?+').replace(':', '?:')
        return converted_string

    def convert_dict(self, row_dict):
        converted_dict = {}
        for key, value in row_dict.iteritems():
            if isinstance(value, dict):
                converted_dict[key] = self.convert_dict(value)
            else:
                converted_dict[key] = self.convert_string(value)
        return converted_dict

    def generate_epl(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("kuehnenagel_generateLabel.epl")
        return template.render(
            auth=body['auth'],
            service=body['service'],
            parcel=body['parcel'],
            sender_address=body['from_address'],
            recipient_address=body['to_address'])

    def generate_parcel_line(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("deposit_slip_line_parcel.txt")
        return template.render(parcel=body['parcel'])

    def generate_footer_line(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("deposit_slip_line_footer.txt")
        return template.render(service=body['service'])

    def generate_deposit_line(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("deposit_slip_line.txt")
        return template.render(
            auth=body['auth'],
            service=body['service'],
            parcel=body['parcel'],
            sender_address=body['from_address'],
            recipient_address=body['to_address'])

    def generate_deposit_slip(self, body):
        body = self.convert_dict(body)
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("deposit_slip.txt")
        return template.render(
            auth=body['auth'],
            service=body['service'],
            sender_address=body['from_address'],
            recipient_address=body['to_address'])
