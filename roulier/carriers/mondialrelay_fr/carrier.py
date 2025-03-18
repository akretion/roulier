# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import zeep

from ...carrier import Carrier, action
from ...exception import CarrierError
from .schema import (
    MondialRelayLabelInput,
    MondialRelayLabelOutput,
    MondialRelayPickupSiteGetInput,
    MondialRelayPickupSiteSearchInput,
    MondialRelayPickupSiteGetOutput,
    MondialRelayPickupSiteSearchOutput,
)
from .constants import STATUSES


class MondialRelay(Carrier):
    __key__ = "mondialrelay_fr"

    __url__ = "https://api.mondialrelay.com/Web_Services.asmx?WSDL"
    __ref__ = "https://storage.mondialrelay.fr/web-service-solution-v514-EN.pdf"
    __ns_prefix__ = "http://www.mondialrelay.fr/webservice/"

    @property
    def client(self):
        client = zeep.Client(wsdl=self.__url__)
        client.set_ns_prefix(None, self.__ns_prefix__)
        return client.service

    def raise_for_status(self, result):
        if "STAT" not in result:
            raise CarrierError(result, "No status returned")
        if result["STAT"] != "0":
            raise CarrierError(result, STATUSES[int(result["STAT"])])

    @action
    def get_label(self, input: MondialRelayLabelInput) -> MondialRelayLabelOutput:
        result = self.client.WSI2_CreationEtiquette(**input.soap())
        self.raise_for_status(result)
        return MondialRelayLabelOutput.from_soap(result)

    @action
    def search_pickup_sites(
        self, input: MondialRelayPickupSiteSearchInput
    ) -> MondialRelayPickupSiteSearchOutput:
        result = self.client.WSI4_PointRelais_Recherche(**input.soap())
        self.raise_for_status(result)
        return MondialRelayPickupSiteSearchOutput.from_soap(result)

    @action
    def get_pickup_site(
        self, input: MondialRelayPickupSiteGetInput
    ) -> MondialRelayPickupSiteGetOutput:
        result = self.client.WSI4_PointRelais_Recherche(**input.soap())
        self.raise_for_status(result)
        return MondialRelayPickupSiteGetOutput.from_soap(result)
