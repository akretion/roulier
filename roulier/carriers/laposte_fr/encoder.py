# -*- coding: utf-8 -*-
"""Transform input to laposte compatible xml."""
import logging
from jinja2 import Environment, PackageLoader
from roulier.exception import InvalidApiInput

_logger = logging.getLogger(__name__)
from roulier.codec import Encoder
from .common import CARRIER_TYPE
from .api import LAPOSTE_LABEL_FORMAT


class LaposteFrEncoder(Encoder):
    """Transform input to laposte compatible xml."""

    _carrier_type = CARRIER_TYPE
    _action = ["get_label"]

    def _get_actions_mapping():
        return {"get_label": "generateLabelRequest"}

    def _extra_input_data_processing(self, input_payload, data):
        data["service"]["labelFormat"] = self.lookup_label_format(
            data["service"]["labelFormat"]
        )
        return data

    def transform_input_to_carrier_webservice(self, data, action):
        env = Environment(
            loader=PackageLoader("roulier", "/carriers/laposte/templates"),
            extensions=["jinja2.ext.with_", "jinja2.ext.autoescape"],
            autoescape=True,
        )

        template = env.get_template("laposte_%s.xml" % action)
        return {
            "body": template.render(
                service=data["service"],
                parcel=data["parcels"][0],
                auth=data["auth"],
                sender_address=data["from_address"],
                receiver_address=data["to_address"],
                customs=data["customs"],
            ),
            "headers": data["auth"],
            "output_format": data["service"]["labelFormat"],
        }

    def lookup_label_format(self, label_format="ZPL"):
        """Get a Laposte compatible format of label.

        args:
            label_format: (str) ZPL or ZPL_10x15_300dpi
        return
            a value taken in LAPOSTE_LABEL_FORMAT
        """
        lookup = {
            "ZPL": "ZPL_10x15_300dpi",
            "DPL": "DPL_10x15_300dpi",
            "PDF": "PDF_10x15_300dpi",
        }
        if label_format in LAPOSTE_LABEL_FORMAT:
            return label_format
        return lookup.get(label_format, "PDF_10x15_300dpi")
