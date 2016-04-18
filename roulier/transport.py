# -*- coding: utf-8 -*-
"""Send a request to a carrier and get the result."""
import abc


class Transport(object):
    """Send a request to a carrier and get the result."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send(self, input):
        """Send a request to a carrier and get the result.

        Args:
            input: carrier specific
        Return:
            carrier specific
        """
        return
