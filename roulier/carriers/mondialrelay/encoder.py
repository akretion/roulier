"""Transform input to MondialRelay compatible xml."""
import logging
from jinja2 import Environment, PackageLoader
from roulier.exception import InvalidApiInput
from hashlib import md5

_logger = logging.getLogger(__name__)
from roulier.codec import Encoder


class MondialRelayEncoderBase(Encoder):
    def _render_template(self, data):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/mondialrelay/templates"),
            extensions=["jinja2.ext.with_", "jinja2.ext.autoescape"],
            autoescape=True,
        )
        template = env.get_template("mondial_relay_action.xml")
        return template.render(**self._get_template_context(data))

    def transform_input_to_carrier_webservice(self, data):
        return {
            "body": self._render_template(data),
            "headers": {
                "accept": "application-xml",
                "content-type": "text/xml",
            },
        }

    def securize_parameters(self, data, parameters):
        login = data["auth"]["login"]
        password = data["auth"]["password"]
        special_texte_param = ""

        if "Texte" in parameters:
            special_texte_param = parameters["Texte"]
            del parameters["Texte"]

        parameters = {"Enseigne": login, **parameters}

        m = md5()
        m.update(
            "".join(
                [str(v) for v in parameters.values() if v is not None] + [password]
            ).encode(
                "iso-8859-1"
            )  # And not utf-8, yes the doc says otherwise
        )

        parameters["Security"] = m.hexdigest().upper()
        parameters["Texte"] = special_texte_param

        return parameters

    def _get_template_context(self, data):
        parameters = self._get_action_parameters(data)
        parameters = self.securize_parameters(data, parameters)

        action = self.SOAP_ACTION
        if isinstance(action, dict):
            action = action[data["service"]["labelFormat"]]

        return {
            "action": action,
            "parameters": parameters,
        }

    def _get_action_parameters(self, data):
        return {}


class MondialRelayEncoderGetLabel(MondialRelayEncoderBase):
    """Transform input to mondialrelay compatible xml."""

    SOAP_ACTION = {"JSON": "WSI2_CreationExpedition", "PDF": "WSI2_CreationEtiquette"}

    def _serialize_address(self, address, prefix):
        return {
            "%s_%s" % (prefix, key): value
            for key, value in {
                "Langage": address["lang"],
                "Ad1": address["name"],
                "Ad2": address["company"],
                "Ad3": address["street1"],
                "Ad4": address["street2"],
                "Ville": address["city"],
                "CP": address["zip"],
                "Pays": address["country"],
                "Tel1": address["phone"],
                "Tel2": address["phone2"],
                "Mail": address["email"],
            }.items()
        }

    def _get_action_parameters(self, data):
        s = data["service"]
        p = data["parcels"][0]

        return {
            "ModeCol": s["pickupMode"],
            "ModeLiv": s["product"],
            "NDossier": s["shippingId"],
            "NClient": s["customerId"],
            **self._serialize_address(data["from_address"], prefix="Expe"),
            **self._serialize_address(data["to_address"], prefix="Dest"),
            "Poids": int(p["weight"] * 1000),
            "Longueur": p["length"],
            "Taille": p["height"],
            "NbColis": p["count"],
            "CRT_Valeur": s["cashOnDelivery"],
            "CRT_Devise": s["cashOnDeliveryCurrency"],
            "Exp_Valeur": s["price"],
            "Exp_Devise": s["currency"],
            "COL_Rel_Pays": s["pickupCountry"],
            "COL_Rel": s["pickupSite"],
            "LIV_Rel_Pays": s["shippingCountry"],
            "LIV_Rel": s["shippingSite"],
            "TAvisage": s["notice"],
            "TReprise": s["takeBack"],
            "Montage": s["assemblyTime"],
            # "TRDV": s["TRDV"], Unused
            "Assurance": s["insurance"],
            "Instructions": s["instructions"],
            "Texte": s["text"],
        }


class MondialRelayEncoderFindPickupSite(MondialRelayEncoderBase):
    """Transform input to mondialrelay compatible xml."""

    SOAP_ACTION = "WSI4_PointRelais_Recherche"

    def _get_action_parameters(self, data):
        s = data["search"]

        return {
            "Pays": s["country"],
            "NumPointRelais": s["id"],
            "CP": s["zip"],
            "Latitude": s["lat"],
            "Longitude": s["lng"],
            "Poids": s["weight"],
            "Action": s["action"],
            "DelaiEnvoi": s["delay"],
            "RayonRecherche": s["searchRadius"],
            "TypeActivite": s["actionType"],
            "NombreResultats": s["resultsCount"],
        }
