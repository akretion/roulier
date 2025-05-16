# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
import re
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

    def _match_city(self, city, suggestions):
        """
        Match the city with the suggestions.
        """

        def _normalize(s):
            return re.sub(r"[-_ ']", "", s.lower())

        city = _normalize(city)

        # Check for exact normalized match
        for suggestion in suggestions:
            if _normalize(suggestion) == city:
                return suggestion

        # Check for inclusive match
        if len(city) > 3:
            for suggestion in suggestions:
                if city in _normalize(suggestion):
                    return suggestion

        # Check for partial match with a levenshtein distance
        # of 2 or less
        def _levenshtein(s1, s2):
            m = len(s1)
            n = len(s2)
            dp = [[0] * (n + 1) for _ in range(m + 1)]
            for i in range(m + 1):
                dp[i][0] = i
            for j in range(n + 1):
                dp[0][j] = j
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1]
                    else:
                        dp[i][j] = min(
                            dp[i - 1][j] + 1,
                            dp[i][j - 1] + 1,
                            dp[i - 1][j - 1] + 1,
                        )
            return dp[m][n]

        distances = [
            _levenshtein(city, _normalize(suggestion)) for suggestion in suggestions
        ]
        min_distance = min(distances)
        min_index = distances.index(min_distance)
        if min_distance <= 2:
            return suggestions[min_index]

        return None

    def _auth(self, auth):
        response = requests.post(f"{self.__url__}/index.php", data=auth.params())
        error = self._xpath_to_text(response, '//td[@class="f_erreur_small"]')
        if error:
            raise CarrierError(response, error)

        return response.cookies

    def _validate(self, auth, params, initial_city=None):
        # 1) Validate
        response = requests.get(
            f"{self.__url__}/corps.php",
            params={"action": "Valider", **params},
            cookies=auth,
        )

        # Handle approximative city
        cp_dest = self._xpath(response, '//select[@name="cp_dest"]')
        if cp_dest:
            cp_dest = cp_dest[0]
            suggestions = [city.text.split(" ", 1)[1] for city in cp_dest.getchildren()]
            initial_city = params["dest_ville"] or initial_city
            city = self._match_city(initial_city, suggestions)
            if not city:
                raise CarrierError(
                    response,
                    f"City {initial_city} not found, "
                    f"available cities are {', '.join(suggestions)}",
                )

            _logger.warning(f"Replacing {initial_city} by {city}")
            params["dest_ville"] = city.encode("latin-1")
            return self._validate(auth, params, initial_city)

        error = self._xpath_to_text(response, '//p[@class="f_erreur"]')
        if error:
            if (
                error == "AUCUNE COMMUNE NE CORRESPOND AUX CRITERES SAISIS"
                and params["dest_ville"]
            ):
                # Try with only the postal code
                _logger.warning(
                    f"City {params['dest_ville']} not found, "
                    f"trying with only the postal code {params['dest_cp']}"
                )
                initial_city = params["dest_ville"]
                params["dest_ville"] = ""
                return self._validate(auth, params, initial_city)

            raise CarrierError(response, error)

    def _print(self, auth, params, format="PDF"):
        # 2) Print
        response = requests.get(
            f"{self.__url__}/corps.php",
            params={
                "action": "Imprimer(PDF)",  # This is only to get the liste_cmd
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

    def _download(self, auth, order, format="PDF"):
        # 3) Get label
        response = requests.get(
            f"{self.__url__}/label_ool.php",
            params={
                "origine": "OOL",
                "output": order["format"] if format == "PDF" else "PRINTER",
                "url_retour": f"{self.__url__}/corps.php?module=cmdjou",
                "liste_cmd": order["order"],
            },
            cookies=auth,
        )
        if format == "EPL":
            # We need to get the file name
            button = self._xpath(response, '//input[@id="btn_imp"]')
            if not button:
                raise CarrierError(response, "No generated EPL found")
            epl_fn = button[0].attrib["onclick"].split("'")[3]
            response = requests.get(f"{self.__url__}/tmp/{epl_fn}", cookies=auth)

        return base64.b64encode(response.content)

    def _get_tracking(self, auth, order, label, input, format="PDF"):
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
                "id": f"{order_ref}_{i + 1}",
                "reference": input.parcels[i].reference,
                "format": format,
                "label": label if i == 0 else None,  # Only the first parcel has
                # the label since the label contains all parcels
                "tracking": trackings[i],
            }
            for i in range(count)
        ]

    @action
    def get_label(self, input: CiblexLabelInput) -> CiblexLabelOutput:
        auth = self._auth(input.auth)
        format = input.service.labelFormat or "PDF"
        if format not in ["PDF", "EPL"]:
            # Website also use "PRINTER" but this can't work here
            raise CarrierError(None, "Only PDF and EPL format are supported")

        # requests send all params as utf-8, but Ciblex expect latin-1
        params = input.params()
        self._validate(auth, params)
        order = self._print(auth, params, format)
        label = self._download(auth, order, format)
        results = self._get_tracking(auth, order, label, input, format)

        return CiblexLabelOutput.from_params(results)
