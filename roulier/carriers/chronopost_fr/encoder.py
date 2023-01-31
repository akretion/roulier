"""Transform input to chronopost compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder


class ChronopostFrEncoder(Encoder):
    def _extra_input_data_processing(self, input_payload, data):
        data["service"]["shippingDate"] = data["service"]["shippingDate"].strftime(
            "%Y/%M/%d"
        )
        return data

    def transform_input_to_carrier_webservice(self, data):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/chronopost_fr/templates"),
            autoescape=True,
        )
        action = self.config.action
        template = env.get_template("chronopost_%s.xml" % action)
        return {
            "body": template.render(
                service=data["service"],
                parcel=data["parcels"][0],
                from_address=data["from_address"],
                # TODO manage customer address different from expeditor
                customer_address=data["from_address"],
                to_address=data["to_address"],
                auth=data["auth"],
            ),
            "output_format": data["service"]["labelFormat"],
        }
