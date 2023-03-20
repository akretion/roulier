"""Transform input to dpd compatible xml."""

from datetime import datetime

from jinja2 import Environment, PackageLoader

from roulier.codec import Encoder
from roulier.exception import InvalidApiInput

DPD_ACTIONS = "createShipmentWithLabels"


class DpdEncoder(Encoder):
    """Transform input to dpd compatible xml."""

    def transform_input_to_carrier_webservice(self, data):
        """Transform input to dpd compatible xml."""

        if data["service"]["product"] == "DPD_Predict":
            data["service"]["notifications"] = "Predict"
        if "pickupLocationId" in data["service"]:
            data["service"]["dropOffLocation"] = data["service"].pop("pickupLocationId")
        data["service"]["shippingDate"] = data["service"]["shippingDate"].strftime(
            "%d/%m/%Y"
        )

        def reduce_address(address):
            """Concat some fields.

            Because there is no street2 nor company in DPD api.
            append street2 to street1 and truncate at 70
            append company to name
            """
            address["street1"] = ("%s, %s" % (address["street1"], address["street2"]))[
                0:70
            ]
            address["name"] = ("%s, %s" % (address["name"], address["company"]))[0:35]

        reduce_address(data["to_address"])
        reduce_address(data["from_address"])

        output_format = data["service"]["labelFormat"]
        is_legacy = data["service"]["legacy"]
        # if data["service"]["labelFormat"] in ("PNG", "ZPL"):
        if data["service"]["labelFormat"] == "PNG":
            # WS doesn't handle zpl yet, we convert it later
            # png is named Default, WTF DPD?
            data["service"]["labelFormat"] = "Default"

        env = Environment(
            loader=PackageLoader("roulier", "carriers/dpd_fr_soap/templates"),
            autoescape=True,
        )

        template = env.get_template("dpd_createShipmentWithLabels.xml")
        return {
            "body": template.render(
                service=data["service"],
                parcel=data["parcels"][0],
                sender_address=data["from_address"],
                receiver_address=data["to_address"],
                legacy=is_legacy,
            ),
            "headers": data["auth"],
            "output_format": output_format,
            "is_legacy": is_legacy,
        }
