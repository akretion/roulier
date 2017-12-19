# -*- coding: utf-8 -*-
"""Implement geodisWS."""
from roulier.transport import Transport
from datetime import datetime
import logging

log = logging.getLogger(__name__)


class GeodisTransportEdi(Transport):
    """Implement Geodis EDI"""

    def send(self, payload):
        """Call this function.

        Args:
            payload.body: XML in a string
            payload.header : auth
        Return:
            {
                response: (Requests.response)
                body: XML response (without soap)
                parts: dict of attachments
            }
        """
        body = payload['body']
        headers = payload['headers']
        message = self.transport_wrap(body, headers)
        return self.convert_to_edi(message)

    def transport_wrap(self, body, headers):
        date = datetime.now()
        return [
            ['UNB', ['UNOA', '3'],
                [headers['interchangeSender'], '22'],
                [headers['interchangeRecipient'], '22'],
                [date.strftime('%d%m%y'), date.strftime('%H%M')],
                headers['depositId']
             ],
        ] + body + [['UNZ', '1', headers['depositId']]]

    def convert_to_edi(self, arr):
        def parse_token(token):
            if isinstance(token, list):
                return ":".join([sanitize(tok) for tok in token])
            else:
                return sanitize(token)

        def parse_segment(segment):
            return "%s'" % "+".join([parse_token(token) for token in segment])

        def parse_lines(lines):
            return "\n".join([parse_segment(segment) for segment in lines])

        def sanitize(token):
            # replace escapable chars by space
            # because, replacing "'" by "?'"
            # increase length of the token
            # which is limited by 35
            sanitized = (
                token
                .replace("?", " ")
                .replace("'", " ")
                .replace("+", " ")
                .replace(":", " ")
            )
            return sanitized

        return parse_lines(arr)
