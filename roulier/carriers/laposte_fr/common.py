# -*- coding: utf-8 -*-
"""Implementation for Laposte."""
from ...roulier import Carrier

CARRIER_TYPE = "laposte_fr"
LAPOSTE_WS = "https://ws.colissimo.fr/sls-ws/SlsServiceWS"


class Laposte(Carrier):
    """Implementation for Laposte."""

    _carrier_type = CARRIER_TYPE
    _action = ["get_label"]
