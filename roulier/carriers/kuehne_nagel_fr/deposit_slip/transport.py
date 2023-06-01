"""Implement for kuehne nagel."""
from roulier.transport import TransportBase
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
from io import BytesIO

import logging

log = logging.getLogger(__name__)


class KuehneNagelFrTransportEDI(TransportBase):
    """Generate EPL offline and txt for EDI."""

    def convert_dict(self, row_dict):
        """
        Concert dict by replacing forbiden characters in strings.
        Add '?' before ?+.' chararacters to be compatible with DISPOR message syntax.
        """
        converted_dict = {}
        for key, value in row_dict.items():
            if isinstance(value, dict):
                converted_dict[key] = self.convert_dict(value)
            elif isinstance(value, str):
                converted_dict[key] = (
                    value.replace("?", "??")
                    .replace("'", "?'")
                    .replace("+", "?+")
                    .replace(":", "?:")
                )
            else:
                converted_dict[key] = value
        return converted_dict

    def get_template(self, template_name):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/kuehne_nagel_fr/templates"),
        )
        template = env.get_template(template_name)
        return template
        return template.render(
            service=body["service"],
            parcel=body["parcel"],
            sender_address=body["from_address"],
            recipient_address=body["to_address"],
        )

    def _get_deposit_line(self, shipment):
        # get global line volume and weight from parcels
        shipment["service"]["volume"] = sum(
            [parcel.get("volume", 0.0) for parcel in shipment["parcels"]]
        )
        shipment["service"]["weight"] = sum(
            [parcel.get("weight", 0.0) for parcel in shipment["parcels"]]
        )
        top_template = self.get_template("deposit_slip_line.txt")
        top_part = top_template.render(
            service=shipment["service"], recipient_address=shipment["to_address"]
        )
        parcel_part = ""
        for parcel in shipment["parcels"]:
            parcel_template = self.get_template("deposit_slip_line_parcel.txt")
            parcel_line = parcel_template.render(parcel=parcel)
            parcel_part += "\n%s" % parcel_line
        footer_template = self.get_template("deposit_slip_line_footer.txt")
        footer_part = footer_template.render(service=shipment["service"])
        deposit_line_part = "%s\n%s\n%s" % (top_part, parcel_part, footer_part)
        return deposit_line_part

    def send(self, body):
        body = self.convert_dict(body)
        lines = []
        for shipment in body["shipments"]:
            lines.append(self._get_deposit_line(shipment))
        body["service"]["lines"] = lines
        template = self.get_template("deposit_slip.txt")
        return template.render(
            auth=body["auth"],
            service=body["service"],
            sender_info=body["sender_info"],
            recipient_info=body["recipient_info"],
        )
