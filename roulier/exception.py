# -*- coding: utf-8 -*-
"""Exception classes"""
import logging

log = logging.getLogger(__name__)


class InvalidApiInput(Exception):
    """Bad input.

    Use this class in your application to manage
    exception with api call
    """


class InvalidAction(Exception):
    """Bad action requested.

    Actions are WS method or else
    """


class CarrierError(Exception):
    """Error from WS.

    Use this class in your application to manage
    exception with the carrier WS
    """
    def __init__(self, response, msg=None):
        if msg is None:
            msg = "An error occured with WS"
        super(CarrierError, self).__init__(msg)
        self.response = response
        if self.response:
            log.debug(response.text)
