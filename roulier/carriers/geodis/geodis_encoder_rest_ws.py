# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .geodis_common_ws import GEODIS_INFOS


class GeodisEncoderRestWs(Encoder):
    def api(self, action):
        api = GEODIS_INFOS[action]["api"]()
        return api.api_values()

    def encode(self, api_input, action):
        api = GEODIS_INFOS[action]["api"]()
        if not api.validate(api_input):
            raise InvalidApiInput("Input error : %s" % api.errors(api_input))
        data = api.normalize(api_input)

        infos = {
            "url": "%s/%s"
            % (GEODIS_INFOS[action]["endpoint"], GEODIS_INFOS[action]["service"],),
            "service": GEODIS_INFOS[action]["service"],
            "action": action,
        }

        return {
            "headers": data["auth"],
            "body": data["service"],
            "infos": infos,
        }
