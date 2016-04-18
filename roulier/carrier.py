# -*- coding: utf-8 -*-
"""Carrier interface."""
import abc


class Carrier(object):
    """Carrier interface."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def api(self):
        """Expose how to communicate with a carrier implementation."""
        return

    @abc.abstractmethod
    def get(self, action):
        """Invoke an action for a carrier."""
        return
