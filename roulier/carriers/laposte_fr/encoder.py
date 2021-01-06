# -*- coding: utf-8 -*-
"""Transform input to laposte compatible xml."""
import logging
from jinja2 import Environment, PackageLoader
from roulier.exception import InvalidApiInput

_logger = logging.getLogger(__name__)
from roulier.codec import Encoder
from .api import LAPOSTE_LABEL_FORMAT


class LaposteFrEncoderBase(Encoder):
    def _render_template(self, data):
        env = Environment(
            loader=PackageLoader("roulier", "/carriers/laposte_fr/templates"),
            extensions=["jinja2.ext.with_", "jinja2.ext.autoescape"],
            autoescape=True,
        )
        template = env.get_template("laposte_%s.xml" % self.config.action)
        return template.render(**self._get_template_context(data))

    def _get_template_context(self, data):
        return {}

    def transform_input_to_carrier_webservice(self, data):
        return {
            "body": self._render_template(data),
            "headers": data["auth"],
        }


class LaposteFrEncoder(LaposteFrEncoderBase):
    """Transform input to laposte compatible xml."""

    def _get_template_context(self, data):
        return {
            "service": data["service"],
            "parcel": data["parcels"][0],
            "auth": data["auth"],
            "sender_address": data["from_address"],
            "receiver_address": data["to_address"],
            "customs": data["parcels"][0].get("customs", False),
        }

    def _extra_input_data_processing(self, input_payload, data):
        data["service"]["labelFormat"] = self.lookup_label_format(
            data["service"]["labelFormat"]
        )
        data["service"]["shippingDate"] = data["service"]["shippingDate"].isoformat()
        # Since multi parcels is not managed for la poste, some informations are expected
        # in service by laposte but are in parcel in roulier.
        parcel = data["parcels"][0]
        if parcel.get("totalAmount"):
            data["service"]["totalAmount"] = parcel["totalAmount"]
        return data

    def transform_input_to_carrier_webservice(self, data):
        transformed_input = super().transform_input_to_carrier_webservice(data)
        transformed_input["output_format"] = data["service"]["labelFormat"]
        return transformed_input

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


class LaposteFrEncoderGetPackingSlip(LaposteFrEncoderBase):
    def _get_template_context(self, data):
        return {
            "auth": data["auth"],
            "parcels_numbers": data.get("parcels_numbers", []),
            "packing_slip_number": data.get("packing_slip_number", None),
        }
