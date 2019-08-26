# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.api import Api


class GeodisApiRestWs(Api):

    def _schemas(self):
        return {
            'service': self._service(),
            'auth': self._auth(),
        }


class GeodisApiTrackingList(GeodisApiRestWs):
    def _service(self):
        schema = {
            "dateDepart": {"type": "string", "default": "", "empty": True},
            "dateDepartDebut": {"type": "string", "default": "", "empty": True},
            "dateDepartFin": {"type": "string", "default": "", "empty": True},
            "noRecepisse": {"type": "string", "default": "", "empty": True},
            "reference1": {"type": "string", "default": "", "empty": True},
            "cabColis": {"type": "string", "default": "", "empty": True},
            "noSuivi": {"type": "string", "default": "", "empty": True},
            "codeSa": {"type": "string", "default": "", "empty": True},
            "codeClient": {"type": "string", "default": "", "empty": True},
            "codeProduit": {"type": "string", "default": "", "empty": True},
            "typePrestation": {"type": "string", "default": "", "empty": True},
            "dateLivraison": {"type": "string", "default": "", "empty": True},
            "refDest": {"type": "string", "default": "", "empty": True},
            "nomDest": {"type": "string", "default": "", "empty": True},
            "codePostalDest": {"type": "string", "default": "", "empty": True},
            "natureMarchandise": {"type": "string", "default": "", "empty": True},
        }
        return schema


class GeodisApiTracking(GeodisApiRestWs):

    def _service(self):
        schema = {
            "refUniExp": {"type": "string", "default": "", "empty": True},
            "noSuivi": {"type": "string", "default": "", "empty": True},
        }
        return schema
