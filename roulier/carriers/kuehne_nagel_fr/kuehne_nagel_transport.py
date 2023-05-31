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
            'zpl': self.render_template(body, "kuehnenagel_generateLabel.zpl"),
            'line': self.render_template(conv_body, "deposit_slip_line.txt"),
            'parcel': self.render_template(conv_body, "deposit_slip_line_parcel.txt"),
            'footer': self.render_template(conv_body, "deposit_slip_line_footer.txt"),
            'parcelNumber': body['parcel']['barcode'],
            'trackingNumber': body['service']['shippingName'],
        }
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": payload,
        }

    def convert_dict(self, row_dict):
        """
        Concert dict by replacing forbiden characters in strings.
        Add '?' before ?+.' chararacters to be compatible with DISPOR message syntax.
        """
        converted_dict = {}
        for key, value in row_dict.iteritems():
            if isinstance(value, dict):
                converted_dict[key] = self.convert_dict(value)
            elif isinstance(value, (str, unicode)):
                converted_dict[key] = value.replace('?', '??').replace("'", "?'").replace('+', '?+').replace(':', '?:')
            else:
                converted_dict[key] = value
        return converted_dict

    def render_template(self, body, template_name):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/kuehne_nagel/templates'),
            extensions=['jinja2.ext.with_'])
        template = env.get_template(template_name)
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
            sender_info=body['sender_info'],
            recipient_info=body['recipient_info'])
