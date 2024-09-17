# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import requests
from lxml.html import fromstring
from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import CiblexLabelInput, CiblexLabelOutput

_logger = logging.getLogger(__name__)


class Ciblex(Carrier):
    __key__ = "ciblex"
    __url__ = "https://secure.extranet.ciblex.fr/extranet/client"

    def _xpath(self, response, xpath):
        root = fromstring(response.text)
        return root.xpath(xpath)

    def _xpath_to_text(self, response, xpath):
        nodes = self._xpath(response, xpath)
        if nodes:
            return "\n".join([e.text_content() for e in nodes])

    def _auth(self, auth):
        response = requests.post(f"{self.__url__}/index.php", data=auth.params())
        error = self._xpath_to_text(response, '//td[@class="f_erreur_small"]')
        if error:
            raise CarrierError(response, error)

        return response.cookies

    def _validate(self, auth, params):
        # 1) Validate
        response = requests.get(
            f"{self.__url__}/corps.php",
            params={"action": "Valider", **params},
            cookies=auth,
        )

        # Handle approximative city
        cp_dest = self._xpath(response, '//select[@name="cp_dest"]')
        if cp_dest:
            good_city = cp_dest[0].getchildren()[0].text.split(" ", 1)[1]
            if params["dest_ville"] == good_city:
                raise CarrierError(response, "City not found")
            _logger.warning(f"Replacing {params['dest_ville']} by {good_city}")
            params["dest_ville"] = good_city.encode("latin-1")
            return self._validate(auth, params)

        error = self._xpath_to_text(response, '//p[@class="f_erreur"]')
        if error:
            raise CarrierError(response, error)

    def _print(self, auth, params, format="PDF"):
        # 2) Print
        response = requests.get(
            f"{self.__url__}/corps.php",
            params={
                "action": (
                    "Imprimer(PDF)" if format == "PDF" else "Imprimer(Thermique)"
                ),
                **params,
            },
            cookies=auth,
        )

        labels = self._xpath(response, '//input[@name="liste_cmd"]')
        if not labels:
            raise CarrierError(response, "No label found")
        if len(labels) > 1:
            raise CarrierError(response, "Multiple labels found")
        label = labels[0]
        order = label.attrib["value"]
        return {
            "order": order,
            "format": format,
        }

    def _download(self, auth, order):
        # 3) Get label
        response = requests.get(
            f"{self.__url__}/label_ool.php",
            params={
                "origine": "OOL",
                "output": order["format"],
                "url_retour": f"{self.__url__}/corps.php?module=cmdjou",
                "liste_cmd": order["order"],
            },
            cookies=auth,
        )
        return base64.b64encode(response.content)

    def _get_tracking(self, auth, order, label, input):
        # 4) Get tracking
        response = requests.get(
            f"{self.__url__}/corps.php",
            params={
                "codecli": "tous",
                "date1": input.service.shippingDate.strftime("%d/%m/%Y"),
                "date2": input.service.shippingDate.strftime("%d/%m/%Y"),
                "etat": 0,
                "cmdsui": "Rechercher",
                "module": "cmdsui",
                "action": "rechercher",
            },
            cookies=auth,
        )
        # Order format is like "04282,17,1,1" : customerId, order, parcel count, ?
        customer_id, order_id, count, _ = order["order"].split(",")

        count = int(count)
        assert count == len(input.parcels), "Parcel count mismatch"

        order_ref = f"{customer_id}-{order_id.zfill(6)}"
        orders = self._xpath(response, '//tr[@class="t_liste_ligne"]')
        order = next(
            filter(lambda o: o.getchildren()[0].text == order_ref, orders), None
        )
        if order is None or not len(order):
            raise CarrierError(response, f"Order {order_ref} not found")

        trackings = [a.text for a in order.getchildren()[4].findall("a")]
        return [
            {
                "id": f"{order_ref}_{i+1}",
                "reference": input.parcels[i].reference,
                "format": "PDF",
                "label": label,  # TODO: Label contain all parcels, split it?
                "tracking": trackings[i],
            }
            for i in range(count)
        ]

    @action
    def get_label(self, input: CiblexLabelInput) -> CiblexLabelOutput:
        auth = self._auth(input.auth)
        format = input.service.labelFormat or "PDF"
        if format != "PDF":
            # Website also use "PRINTER" but this can't work here
            raise CarrierError(None, "Only PDF format is supported")

        # requests send all params as utf-8, but Ciblex expect latin-1
        params = input.params()
        self._validate(auth, params)
        order = self._print(auth, params, format)
        label = self._download(auth, order)
        results = self._get_tracking(auth, order, label, input)

        return CiblexLabelOutput.from_params(results)
