# -*- coding: utf-8 -*-
"""Fake implementation of dummy."""
from roulier.transport import Transport


class DummyTransport(Transport):
    """Mock class because we generate ZPL inhouse."""

    STATUS_SUCCESS = "Success"

    def send(self, body):
        """Call this function.

        Args:
            body: ZPL in a string
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (None)
                response: (None)
                payload: usefull payload (if success) (body as string)

            }
        """
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": body,
        }
