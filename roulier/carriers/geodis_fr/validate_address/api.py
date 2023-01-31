"""Implementation of Geodis Ws Api."""
from roulier.api import ApiParcel


class GeodisApiFindLocaliteWs(ApiParcel):
    def _address(self):
        schema = super()._address()
        schema["country"].update({"required": True, "empty": False})
        return {
            "country": schema["country"],
            "zip": schema["zip"],
            "city": schema["city"],
        }

    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"]["required"] = False
        # 'description': 'Use test Ws'
        return schema

    def _schemas(self):
        return {
            "auth": self._auth(),
            "to_address": self._address(),
        }
