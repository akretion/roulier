"""Transform input to geodis compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .geodis_common_ws import GEODIS_INFOS


GEODIS_ACTIONS = GEODIS_INFOS.keys()


class GeodisEncoderWs(Encoder):
    """Transform input to geodis compatible xml."""

    def get_api(self, action):
        """Get Api object based on action.

        raise if action is not known"""
        if not (action in GEODIS_ACTIONS):
            raise InvalidApiInput(
                "action %s not in %s" % (action, ", ".join(GEODIS_INFOS))
            )

        return GEODIS_INFOS[action]["api"]()

    def encode(self, api_input, action):
        """Transform input to geodis compatible xml."""
        api = self.get_api(action)
        if not api.validate(api_input):
            raise InvalidApiInput("Input error : %s" % api.errors(api_input))
        env = Environment(
            loader=PackageLoader("roulier", "carriers/geodis/templates"),
            autoescape=True,
        )
        template = env.get_template("geodis_%s.xml" % action)

        data = api.normalize(api_input)
        infos = {
            "xmlns": GEODIS_INFOS[action]["xmlns"],
            "url": (
                data["service"]["is_test"]
                and GEODIS_INFOS[action]["endpoint_test"]
                or GEODIS_INFOS[action]["endpoint"]
            ),
            "action": action,
        }

        def request_impression_etiquette():
            infos["output_format"] = (api_input["service"]["labelFormat"],)
            data["service"]["labelFormat"] = self.lookup_label_format(
                data["service"]["labelFormat"]
            )
            data["service"]["shippingDate"] = data["service"]["shippingDate"].strftime(
                "%Y%M%d"
            )
            data["from_address"]["departement"] = data["from_address"]["zip"][:2]
            return {
                "body": template.render(
                    service=data["service"],
                    parcels=data["parcels"],
                    sender_address=data["from_address"],
                    receiver_address=data["to_address"],
                    xmlns=infos["xmlns"],
                ),
                "headers": data["auth"],
                "infos": infos,
            }

        def request_find_localite():
            return {
                "body": template.render(
                    receiver_address=data["to_address"],
                    xmlns=infos["xmlns"],
                ),
                "headers": data["auth"],
                "infos": infos,
            }

        if action == "demandeImpressionEtiquette":
            return request_impression_etiquette()
        elif action == "findLocalite":
            return request_find_localite()

    def api(self, action="demandeImpressionEtiquette"):
        """Provide a dict prefilled with default values."""
        return self.get_api(action).api_values()

    def lookup_label_format(self, label_format="ZPL"):
        """Get a Geodis compatible format of label.

        args:
            label_format: (str) ZPL or PDF
        return
            a value taken in GEODIS_LABEL_FORMAT
        """
        lookup = {
            "ZPL": "Z",
            "PDF": "P",
            "HTML": "H",
            "XML": "X",
            "EPL2": "E",
            "Z": "Z",
            "P": "P",
            "H": "H",
            "X": "X",
            "E": "E",
        }
        return lookup.get(label_format.upper(), "Z")
