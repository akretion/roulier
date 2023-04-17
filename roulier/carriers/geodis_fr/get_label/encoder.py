"""Transform input to geodis compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput


class GeodisFrParcelEncoder(Encoder):
    """Transform input to geodis compatible xml."""

    def _extra_input_data_processing(self, input_payload, data):
        data["service"]["shippingDate"] = data["service"]["shippingDate"].strftime(
            "%Y%m%d"
        )
        data["from_address"]["departement"] = data["from_address"]["zip"][:2]
        data["service"]["labelFormat"] = self.config.label_formats.get(
            data["service"]["labelFormat"]
        )[0]
        # Hopefully temporary patch : Geodis does not accept dash  : "-" in the name
        # of belgium cities like Braine-le-Chateau
        if data["to_address"].get("country", "") == "BE" and "-" in data[
            "to_address"
        ].get("city", ""):
            data["to_address"]["city"] = data["to_address"]["city"].replace("-", " ")
        return data

    def transform_input_to_carrier_webservice(self, data):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/geodis_fr/templates"),
            autoescape=True,
        )
        action = self.config.action
        template = env.get_template("geodis_%s.xml" % action)
        return {
            "body": template.render(
                service=data["service"],
                parcels=data["parcels"],
                sender_address=data["from_address"],
                receiver_address=data["to_address"],
                xmlns=self.config.xmlns,
            ),
            "headers": data["auth"],
        }
