"""MondialRelay XML -> Python."""
from datetime import time
from lxml import objectify

from ...codec import DecoderGetLabel
import base64


class _UNSPECIFIED:
    pass


def _get_text(xml, tag, default=_UNSPECIFIED):
    """
    Returns the text content of a tag to avoid returning an lxml instance
    If no default is specified, it will raises the original exception of accessing
    to an inexistant tag
    """
    if not hasattr(xml, tag):
        if default is _UNSPECIFIED:
            # raise classic attr error
            return getattr(xml, tag)
        return default
    return getattr(xml, tag).text


def _get_cid(tag, tree):
    element = tree.find(tag)
    if element is None:
        return None
    href = element.getchildren()[0].attrib["href"]
    # href contains cid:236212...-38932@cfx.apache.org
    return href[len("cid:") :]  # remove prefix


class MondialRelayDecoderFindPickupSite(object):
    def __init__(self, config_object):
        """
        pickup_sites are represented in this form:
        {
            "id": 1,
            "name": "",
            "street": "",
            "zip": "",
            "city": "",
            "country": "",
            "lat": "",
            "lng": "",
            "actionType": "",
            "hours": {
                "monday": [time(9, 30), time(12, 30), time(15, 30), time(17, 30)],
                "tuesday": [time(9, 30), time(17, 30)],
                "wednesday": [],
                "thursday": [time(9, 30), time(17, 30)],
                "friday": [time(9, 30), time(17, 30)],
                "saturday": [time(9, 30), time(12, 30)],
                "sunday": [],
            },
            "url_pic": "",
            "url_map": ""
        }
        """
        self.config = config_object
        self.result = {
            "pickup_sites": [],
        }

    def decode(self, response, payload):
        body = response["body"]
        xml = objectify.fromstring(body)
        pickup_sites = xml.xpath(
            "//mr:PointRelais_Details",
            namespaces={"mr": "http://www.mondialrelay.fr/webservice/"},
        )

        def extract_time(node):
            times = [
                int(t)
                for t in node.xpath(
                    ".//mr:string",
                    namespaces={"mr": "http://www.mondialrelay.fr/webservice/"},
                )
                if t
            ]

            return [time(t // 100, t - (t // 100) * 100) for t in times]

        def get_str(s):
            return str(s).strip()

        for pickup_site in pickup_sites:
            self.result["pickup_sites"].append(
                {
                    "id": 1,
                    "name": "\n".join(
                        map(get_str, (pickup_site.LgAdr1, pickup_site.LgAdr2))
                    ),
                    "street": "\n".join(
                        map(get_str, (pickup_site.LgAdr3, pickup_site.LgAdr4))
                    ),
                    "zip": get_str(pickup_site.CP),
                    "city": get_str(pickup_site.Ville),
                    "country": get_str(pickup_site.Pays),
                    "lat": get_str(pickup_site.Latitude),
                    "lng": get_str(pickup_site.Longitude),
                    "actionType": get_str(pickup_site.TypeActivite),
                    "hours": {
                        "monday": extract_time(pickup_site.Horaires_Lundi),
                        "tuesday": extract_time(pickup_site.Horaires_Mardi),
                        "wednesday": extract_time(pickup_site.Horaires_Mercredi),
                        "thursday": extract_time(pickup_site.Horaires_Jeudi),
                        "friday": extract_time(pickup_site.Horaires_Vendredi),
                        "saturday": extract_time(pickup_site.Horaires_Samedi),
                        "sunday": extract_time(pickup_site.Horaires_Dimanche),
                    },
                    "url_pic": get_str(pickup_site.URL_Photo),
                    "url_map": get_str(pickup_site.URL_Plan),
                }
            )


class MondialRelayDecoderGetLabel(DecoderGetLabel):
    """MondialRelay XML -> Python."""

    def decode(self, response, input_payload):
        """MondialRelay XML -> Python."""
        is_pdf = "WSI2_CreationEtiquette" in input_payload["body"]
        xpath = (
            "WSI2_CreationEtiquetteResult"
            if is_pdf
            else "WSI2_CreationExpeditionResult"
        )

        body = response["body"]
        xml = objectify.fromstring(body)
        expeditions = xml.xpath(
            "//mr:%s" % xpath,
            namespaces={"mr": "http://www.mondialrelay.fr/webservice/"},
        )
        for expedition in expeditions:
            parcel = {}
            if is_pdf:
                parcel = {
                    "label": {
                        "data": "https://www.mondialrelay.com"
                        + expedition.URL_Etiquette,
                        "name": "label_url",
                        "type": "url",
                    }
                }
            else:
                parcel = {
                    "barCodes": [
                        str(t)
                        for t in expedition.CodesBarres.xpath(
                            ".//mr:string",
                            namespaces={"mr": "http://www.mondialrelay.fr/webservice/"},
                        )
                        if t
                    ],
                    "tracking": {
                        "agency": {
                            "id": expedition.TRI_AgenceCode,
                            "name": expedition.TRI_Agence,
                        },
                        "group": expedition.TRI_Groupe,
                        "shippingMode": expedition.TRI_LivraisonMode,
                        "shuttle": expedition.TRI_Navette,
                        "tourId": expedition.TRI_TourneeCode,
                    },
                }

            self.result["parcels"].append({"id": expedition.ExpeditionNum, **parcel})
