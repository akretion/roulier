"""Implementation of Geodis Api."""
from roulier.api import BaseApi


class GeodisApiRestWs(BaseApi):
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


class GeodisMappingIn(BaseApi):
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


class GeodisMappingOut(BaseApi):
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
