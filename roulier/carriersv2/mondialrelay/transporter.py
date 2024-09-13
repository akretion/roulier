# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import zeep

from ..api import Transporter, action
from ...exception import CarrierError
from .schema import (
    MondialRelayLabelInput,
    MondialRelayLabelOutput,
    MondialRelayPickupSiteInput,
    MondialRelayPickupSiteOutput,
)
from .constants import STATUSES


class MondialRelay(Transporter):
    __key__ = "mondialrelay2"
    __url__ = "https://api.mondialrelay.com/Web_Services.asmx?WSDL"
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
    def find_pickup_site(
        self, input: MondialRelayPickupSiteInput
    ) -> MondialRelayPickupSiteOutput:
        result = self.client.WSI4_PointRelais_Recherche(**input.soap())
        self.raise_for_status(result)
        return MondialRelayPickupSiteOutput.from_soap(result)
