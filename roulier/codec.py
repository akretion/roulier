# -*- coding: utf-8 -*-
"""Transform to/from a carrier specific format."""
import abc


class Encoder(object):
    """Transform to a carrier specific format.

    For preparing (encode) a request to a carrier for stuff like a label
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def encode(self, input):
        """Transform an oject to carrier specific like XML or EDI.

        Args:
            input: python dict
        Return:
            Specific representation of a request of the carrier
        """
        return


class Decoder(object):
    """Transform from a carrier specific format to dict."""

    @abc.abstractmethod
    def decode(self, answer):
        """Transform a specific representation to python dict.

        Args:
            answer: specific representation of an response of the carrier
        Return:
            Python dict
        """
        return
