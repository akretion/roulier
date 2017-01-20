# -*- coding: utf-8 -*-
"""Implementation for trs."""
from roulier.transport import Transport
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
import unicodecsv as csv
from io import BytesIO


class TrsTransport(Transport):
    """Generate ZPL offline and csv for EDI."""

    STATUS_SUCCESS = "Success"

    def send(self, payload):
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
        body = payload['body']
        label = self.generate_zpl(body)
        attachment = self.map_delivery_line(body)
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": label,
            "attachment": attachment
        }

    def generate_zpl(self, body):
        env = Environment(
            loader=PackageLoader('roulier', '/carriers/trs/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("trs_generateLabel.zpl")
        return template.render(
            service=body['service'],
            parcel=body['parcel'],
            from_address=body['from_address'],
            to_address=body['to_address'])

    def map_delivery_line(self, body):
        data = OrderedDict([
            (u'client', body['from_address']['company']),
            (u'siret', None),
            (u'refCommande', body['service']['reference1']),
            (u'dateEnlevement', body['service']['shippingDate']),
            (u'cr', None),
            (u'va', None),
            (u'nom', body['to_address']['name']),
            (u'adr1', body['to_address']['street1']),
            (u'adr2', body['to_address']['street2']),
            (u'cp', body['to_address']['zip']),
            (u'ville', body['to_address']['city']),
            (u'telephone', body['to_address']['phone']),
            (u'mobile', body['to_address']['phone']),
            (u'email', body['to_address']['email']),
            (u'refDest', body['service']['reference1']),
            (u'commentLiv', None),
            (u'nbConducteurs', None),
            (u'Poids', '%.f' % (body['parcel']['weight'] * 1000)),  # kg to g
            (u'nbColis', 1),  # one row per parcel
            (u'qtéFacturée1', None),
            (u'qtéFacturée2', None),
            (u'qtéFacturée3', None),
            (u'qtéFacturée4', None),
            (u'qtéFacturée5', None),
            (u'qtéFacturée6', None),
            (u'qtéFacturée7', None),
            (u'qtéFacturée8', None),
            (u'qtéFacturée9', None),
            (u'qtéFacturée10', None),
            (u'article1', None),
            (u'article2', None),
            (u'article3', None),
            (u'article4', None),
            (u'article5', None),
            (u'article6', None),
            (u'article7', None),
            (u'article8', None),
            (u'article9', None),
            (u'article10', None),
            (u'regroupement', None),
            (u'refComfour', None),
            (u'codeBarre', body['service']['shippingId']),
            (u'descColis', None),
            (u'porteur', None),
            (u'jourLivraison', None),
        ])
        return data

    def generate_deposit_slip(self, rows):
        output = BytesIO()

        # l'ordre est important
        headers = rows[0].keys()

        # l'ordre est fixé par headers
        writer = csv.DictWriter(output, headers, encoding='utf-8')
        writer.writeheader()
        writer.writerows(rows)
        return output
