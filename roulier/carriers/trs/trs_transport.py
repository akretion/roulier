# -*- coding: utf-8 -*-
"""Implementation for trs."""
from roulier.transport import Transport
from jinja2 import Environment, PackageLoader
from collections import OrderedDict


class TrsTransport(Transport):
    """Generate ZPL offline and csv for EDI."""

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
        payload = {
            'zpl': self.generate_zpl(body),
            'meta': self.map_delivery_line(body),
        }
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": payload,
        }

    def generate_zpl(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/trs/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("trs_generateLabel.zpl")
        return template.render(
            auth=body['auth'],
            service=body['service'],
            outputFormat=body['output_format'],
            parcel=body['parcel'],
            sender_address=body['sender_address'],
            receiver_address=body['receiver_address'])

    def map_delivery_line(self, body):
        data = OrderedDict([
            ('client', body['sender_address']['companyName']),
            ('siret', None),
            ('refCommande', body['service']['shippingReference']),
            ('dateEnlevement', body['service']['shippingDate']),
            ('cr', None),
            ('va', None),
            ('nom', body['receiver_address']['name']),
            ('adr1', body['receiver_address']['street1']),
            ('adr2', body['receiver_address']['street2']),
            ('cp', body['receiver_address']['zipCode']),
            ('ville', body['receiver_address']['city']),
            ('telephone', body['receiver_address']['phoneNumber']),
            ('mobile', body['receiver_address']['phoneNumber']),
            ('email', body['receiver_address']['email']),
            ('refDest', None),
            ('commentLiv', None),
            ('nbConducteurs', None),
            ('Poids', body['parcel']['weight']),
            ('nbColis', None),
            ('qtéFacturée1', None),
            ('qtéFacturée2', None),
            ('qtéFacturée3', None),
            ('qtéFacturée4', None),
            ('qtéFacturée5', None),
            ('qtéFacturée6', None),
            ('qtéFacturée7', None),
            ('qtéFacturée8', None),
            ('qtéFacturée9', None),
            ('qtéFacturée10', None),
            ('article1', None),
            ('article2', None),
            ('article3', None),
            ('article4', None),
            ('article5', None),
            ('article6', None),
            ('article7', None),
            ('article8', None),
            ('article9', None),
            ('article10', None),
            ('regroupement', None),
            ('refComfour', None),
            ('codeBarre', body['parcel']['barcode']),
            ('descColis', None),
            ('porteur', None),
            ('jourLivraison', None),
        ])
        return data

    def generate_delivery_slip(self, rows):
        import csv
        try:
            from cStringIO import StringIO
        except ImportError:
            import StringIO

        output = StringIO()

        # l'ordre est important
        headers = rows[0].keys()

        # l'ordre est fixé par headers
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(rows)
        return output


