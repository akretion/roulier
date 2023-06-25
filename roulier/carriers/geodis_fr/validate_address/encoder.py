"""Transform input to geodis compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput


class GeodisFrFindLocaliteEncoder(Encoder):
    """Transform input to geodis compatible xml."""

    def transform_input_to_carrier_webservice(self, data):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/geodis_fr/templates"),
            autoescape=True,
        )
        action = self.config.action
        template = env.get_template("geodis_%s.xml" % action)
        return {
            "body": template.render(
                receiver_address=data["to_address"],
                xmlns=self.config.xmlns,
            ),
            "headers": data["auth"],
        }
