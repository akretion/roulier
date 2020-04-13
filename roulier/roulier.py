# -*- coding: utf-8 -*-
"""Factory of main classes."""

from .codec import Encoder, Decoder
from .api import Api
from .transport import Transport
from .tools import get_subclass


# generic method which call the right action on the right class.
def get(action, carrier_type, *args):
    myclass = get_subclass(Carrier, carrier_type, action)
    return getattr(myclass, action)(carrier_type, action, *args)


def get_carriers():
    """Get name of available carriers.

    return: list of strings
    """
    return [
        'laposte_fr',
        'chronopost_fr',
    ]


def get_schema(action, carrier_type):
    carrier_api = get_subclass(Api, carrier_type, action)()
    return getattr(carrier_api, 'api_schema')()


class Carrier(object):
    _carrier_type = None
    _action = []


    @classmethod
    def get_label(cls, carrier_type, action, data):
        encoder = get_subclass(Encoder, carrier_type, action)()
        decoder = get_subclass(Decoder, carrier_type, action)()
        transport = get_subclass(Transport, carrier_type, action)()

        payload = encoder.encode(data, action)
        response = transport.send(payload)
        return decoder.decode(response, payload)

    def get_tracking_link(carrier_type, action, data):
        # nothing generic todo?
        pass
