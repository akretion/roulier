# -*- coding: utf-8 -*-
"""Factory of main classes."""
from carriers.laposte.laposte import Laposte
from carriers.dummy.dummy import Dummy


def get(carrier):
    """Get a 1 method carrier implementation.

    If you need more, like only encode or only transport
    (Webservice), instanciate class directly like:
    from roulier.carriers.laposte import LaposteTransport
    ws = LaposteTransport()
    ws.send(data)
    """
    carriers = {
        "laposte": Laposte,
        "dummy": Dummy,
    }
    carrier_obj = carriers.get(carrier.lower())

    if carrier_obj:
        return carrier_obj()
    else:
        raise BaseException("Carrier not found")
