"""Implementation of Geodis Api."""
from ..geodis_rest_api import GeodisMappingIn, GeodisApiRestWs, GeodisMappingOut


class GeodisApiTrackingListMapping(GeodisMappingIn):
    """Internal API

    Used to rename and coerce fields"""

    def _schemas(self):
        def dt_to_string(dt):
            return dt.strftime("%Y-%m-%d")

        return {
            "service": {
                "shippingDate": {
                    "type": "string",
                    "rename": "dateDepart",
                    "coerce": dt_to_string,
                },
                "shippingDateStart": {
                    "type": "string",
                    "rename": "dateDepartDebut",
                    "coerce": dt_to_string,
                },
                "shippingDateEnd": {
                    "type": "string",
                    "rename": "dateDepartFin",
                    "coerce": dt_to_string,
                },
                # make date as string
                "dateDepart": {"type": "string", "coerce": dt_to_string},
                "dateDepartDebut": {"type": "string", "coerce": dt_to_string},
                "dateDepartFin": {"type": "string", "coerce": dt_to_string},
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
        return {
            "service": {
                "trackingId": {"rename": "noSuivi"},
            }
        }


class GeodisApiTracking(GeodisApiRestWs):
    def _service(self):
        schema = {
            "refUniExp": {"type": "string", "default": "", "empty": True},
            "trackingId": {"type": "string", "default": "", "empty": True},
        }
        return schema

    def _interal_api(self):
        return GeodisApiTrackingMapping(self.config)


class GeodisApiTrackingList(GeodisApiRestWs):
    def _service(self):
        return {
            "shippingDate": {"type": "date", "empty": True},
            "shippingDateStart": {"type": "date", "empty": True},
            "shippingDateEnd": {"type": "date", "empty": True},
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
        schema = super()._schemas()
        schema["tracking"] = self._tracking()
        schema["to_address"] = self._to_address()
        return schema

    def _interal_api(self):
        return GeodisApiTrackingListMapping(self.config)


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
