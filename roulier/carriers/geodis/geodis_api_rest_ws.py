# -*- coding: utf-8 -*-
"""Implementation of Geodis Api."""
from roulier.api import Api


class GeodisApiRestWs(Api):
    def _schemas(self):
        return {
            "service": self._service(),
            "auth": self._auth(),
        }

    def normalize(self, data):
        externalApi = super(GeodisApiRestWs, self)
        internalApi = self._interal_api()
        step1 = externalApi.normalize(data)
        step2 = internalApi.normalize(step1)
        return step2

    def api_values(self):
        """Return a dict containing expected keys.

        It's a normalized version of the schema.
        only internal api
        """
        return self._validator().normalized({}, self.api_schema())

    def _interal_api(self):
        pass


class GeodisMappingIn(Api):
    """Internal API"""

    def flatten(self, data, out):
        for (key, val) in data.items():
            if isinstance(val, dict):
                self.flatten(val, out)
            else:
                out[key] = val

    def normalize(self, data):
        without_auth = {key: val for (key, val) in data.items() if key != "auth"}
        flat = {"auth": data["auth"], "service": {}}
        self.flatten(without_auth, flat["service"])
        normalized = super(GeodisMappingIn, self).normalize(flat)
        return normalized


class GeodisApiTrackingListMapping(GeodisMappingIn):
    """Internal API

    Used to rename fields."""

    def _schemas(self):
        return {
            "service": {
                "shippingDate": {"rename": "dateDepart"},
                "shippingDateStart": {"rename": "dateDepartDebut"},
                "shippingDateEnd": {"rename": "dateDepartFin"},
                "agencyId": {"rename": "codeSa"},
                "customerId": {"rename": "codeClient"},
                "reference1": {"rename": "reference1"},
                "reference2": {"rename": "refDest"},
                "name": {"rename": "nomDest"},
                "zip": {"rename": "codePostalDest"},
                "estDeliveryDate": {"rename": "dateLivraison"},
                "shippingId": {"rename": "noRecepisse"},
                "barcode": {"rename": "cabColis"},
                "trackingId": {"rename": "noSuivi"},
            }
        }


class GeodisApiTrackingMapping(GeodisMappingIn):
    """Internal API

    Used to rename fields."""

    def _schemas(self):
        return {"service": {"trackingId": {"rename": "noSuivi"},}}


class GeodisApiTracking(GeodisApiRestWs):
    def _service(self):
        schema = {
            "refUniExp": {"type": "string", "default": "", "empty": True},
            "trackingId": {"type": "string", "default": "", "empty": True},
        }
        return schema

    def _interal_api(self):
        return GeodisApiTrackingMapping()


class GeodisApiTrackingList(GeodisApiRestWs):
    def _service(self):
        return {
            "shippingDate": {"type": "string", "default": "", "empty": True},
            "shippingDateStart": {"type": "string", "default": "", "empty": True},
            "shippingDateEnd": {"type": "string", "default": "", "empty": True},
            "agencyId": {"type": "string", "default": "", "empty": True},
            "customerId": {"type": "string", "default": "", "empty": True},
            "reference1": {"type": "string", "default": "", "empty": True},
            "reference2": {"type": "string", "default": "", "empty": True},
        }

    def _tracking(self):
        return {
            "estDeliveryDate": {"type": "string", "default": "", "empty": True},
            "shippingId": {"type": "string", "default": "", "empty": True},
            "barcode": {"type": "string", "default": "", "empty": True},
            "trackingId": {"type": "string", "default": "", "empty": True},
        }

    def _to_address(self):
        return {
            "name": {"type": "string", "default": "", "empty": True},
            "zip": {"type": "string", "default": "", "empty": True},
        }

    def _schemas(self):
        schema = super(GeodisApiTrackingList, self)._schemas()
        schema["tracking"] = self._tracking()
        schema["to_address"] = self._to_address()
        return schema

    def _interal_api(self):
        return GeodisApiTrackingListMapping()


class GeodisMappingOut(Api):
    def normalize(self, data):
        schema = self.schema()
        # self.add_tracking_code(data)
        return self.visit(data, schema)

    def visit(self, data, schema):
        out = {}
        for (key, val) in schema.items():
            if isinstance(val, dict):
                out[key] = self.visit(data, val)
            else:
                out[key] = data[val]
        return out


class GeodisApiTrackingListOut(GeodisMappingOut):
    def to_address(self):
        return {
            "street1": "adresse1Dest",
            "street2": "adresse2Dest",
            "country": "codePaysDest",
            "zip": "codePostalDest",
            "country_name": "libellePaysDest",
            "name": "nomDest",
            "city": "villeDest",
        }

    def from_address(self):
        return {
            "street1": "adresse1Exp",
            "street2": "adresse2Exp",
            "country": "codePaysExp",
            "zip": "codePostalExp",
            "country_name": "libellePaysExp",
            "name": "nomExp",
            "city": "villeExp",
        }

    def parcels(self):
        return {
            "weight": "poids",
        }

    def service(self):
        return {
            "product": "codeProduit",
            "agencyId": "codeSa",
            "customerId": "codeClient",
            "shippingId": "noRecepisse",
            "shippingDate": "dateDepart",
            "reference1": "reference1",
            "reference2": "reference2",
            "reference3": "refDest",
            "option": "codeOption",
        }

    def tracking(self):
        return {
            "statusDate": "dateEtat",
            "estDeliveryDate": "dateLivraison",
            "status": "status",
            "statusDetails": "libelleLongEtat",
            "trackingCode": "noSuivi",
            "publicUrl": "urlSuiviDestinataire",
            "proofUrl": "urlImageEnlevementLivraison",
        }

    def schema(self):
        return {
            "parcels": self.parcels(),
            "service": self.service(),
            "from_address": self.from_address(),
            "to_address": self.to_address(),
            "tracking": self.tracking(),
        }
