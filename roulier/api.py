"""API interface."""
from cerberus import Validator
from unidecode import unidecode


class MyValidator(Validator):
    """Custom validator."""

    def _normalize_coerce_zpl(self, value):
        """Sanitze input for ZPL.

        Remove ZPL ctrl caraters
        Remove accents
        """
        if not isinstance(value, str):
            return value

        ctrl_cars = [
            0xFE,  # Tilde ~
            0x5E,  # Caret ^
            0x1E,  # RS (^ substitution)
            0x10,  # DLE (~ substitution)
        ]
        val = unidecode(value)
        for ctrl in ctrl_cars:
            val = val.replace("%c" % ctrl, "")
        return val

    def _normalize_coerce_accents(self, value):
        """Sanitize accents for some WS."""
        if not isinstance(value, str):
            return value
        sanitized = (
            (
                value
                # quick and dirty replacement
                # of common accentued chars in french
                # because some ws don't handle well utf8
                .replace("é", "e")
                .replace("è", "e")
                .replace("ë", "e")
                .replace("ê", "e")
                .replace("ô", "o")
                .replace("ï", "i")
                .replace("ö", "o")
                .replace("à", "a")
                .replace("â", "a")
                .replace("ç", "c")
                .replace("û", "u")
                .replace("ù", "u")
                .replace("É", "E")
                .replace("È", "E")
                .replace("Ë", "E")
                .replace("Ê", "E")
                .replace("Ô", "O")
                .replace("Ï", "I")
                .replace("Ö", "O")
                .replace("À", "A")
                .replace("Â", "A")
                .replace("Ç", "C")
                .replace("Û", "U")
                .replace("Ù", "U")
                .replace("œ", "oe")
                .replace("Œ", "OE")
            )
            .encode("ascii", "ignore")
            .decode("ascii")
        )  # cut remaining chars
        return sanitized


class BaseApi(object):
    def __init__(self, config_object):
        self.config = config_object

    def _validator(self):
        v = MyValidator()
        v.allow_unknown = True
        # v.purge_unknown = True
        return v

    def _auth(self):
        return {
            "login": {"type": "string", "default": ""},
            "password": {"type": "string", "default": ""},
            "isTest": {"type": "boolean", "default": False},
        }

    def api_schema(self):
        """Return the expected schema of the api.

        A validation schema is a mapping, usually a dict.
        Schema keys are the keys allowed in the target dictionary.
        Schema values express the rules that must be matched
        by the corresponding target values.

        See http://docs.python-cerberus.org/en/stable/schemas.html

        """
        v = self._validator()
        schemas = self._schemas()

        def wrap_schema(schema):
            # if schema is a simple dict, wrap it as a dict
            # else this work has already be done
            # like it's a list
            if "schema" in schema or "items" in schema:
                return schema
            return {
                "schema": schema,
                "default": schema.get("default") or v.normalized({}, schema),
                "type": schema.get("type", "dict"),
            }

        return {s: wrap_schema(schemas[s]) for s in schemas}

    def api_values(self):
        """Return a dict containing expected keys.

        It's a normalized version of the schema.
        """
        return self.normalize({})

    def errors(self, data):
        """Return validation errors."""
        v = self._validator()
        v.validate(data, self.api_schema())
        return v.errors

    def validate(self, data):
        """Ensure the data are valid.

        returns: bool

        See also errors()
        """
        return self._validator().validate(data, self.api_schema())

    def normalize(self, data):
        """Retrurn a normalized dict based on input.

        See http://docs.python-cerberus.org/en/stable/usage.html
        """
        return self._validator().normalized(data, self.api_schema())


class ApiParcel(BaseApi):
    """Define expected fields of carriers.

    This class should be overriden by each carrier.
    """

    def _address(self):
        return {
            "company": {"type": "string", "default": ""},
            "name": {"type": "string", "default": "", "required": True, "empty": False},
            "street1": {"type": "string", "default": ""},
            "street2": {"type": "string", "default": ""},
            "country": {"type": "string", "default": ""},
            # , 'description': 'ISO 3166-1 alpha-2 '},
            "city": {"type": "string", "default": ""},
            "zip": {"type": "string", "default": ""},
            "phone": {"type": "string", "default": ""},
            "email": {"type": "string", "default": ""},
        }

    def _from_address(self):
        address = self._address()
        return address

    def _to_address(self):
        address = self._address()
        address["street1"].update({"required": True, "empty": False})
        address["country"].update({"required": True, "empty": False})
        address["city"].update({"required": True, "empty": False})
        address["zip"].update({"required": True, "empty": False})
        return address

    def _parcel(self):
        return {
            "weight": {
                "type": "float",
                "default": "",
                "required": True,
                "empty": False,
            },
            # reference of parcel in external app
            # This ref should be attached to the label in roulier response so the
            # external app is able to link a label file/tracking ref to the corresponding
            # parcel.
            "reference": {"type": "string"},
        }
        # 'description': 'Weight in kg',

    def _parcels(self):
        return {
            "type": "list",
            "schema": {"schema": self._parcel(), "type": "dict"},
        }

    def _service(self):
        return {
            "product": {"default": ""},
            "agencyId": {"default": ""},
            "customerId": {"default": ""},
            "shippingId": {"default": ""},
            "shippingDate": {
                "type": "date",
                "required": True,
                "empty": False,
            },
            # 'description': 'Additionnal info visible by the client. Example : order number'
            "reference1": {"type": "string", "default": ""},
            "reference2": {"type": "string", "default": ""},
            "reference3": {"type": "string", "default": ""},
            # 'description': 'Format of output (usually pdf or zpl)'
            "labelFormat": {"default": ""},
            # 'description': 'Additionnal instructions for delivery',
            "instructions": {"default": ""},
        }

    def _schemas(self):
        return {
            "service": self._service(),
            "auth": self._auth(),
            "parcels": self._parcels(),
            "from_address": self._from_address(),
            "to_address": self._to_address(),
        }


class ApiPackingSlip(BaseApi):
    def _packing_slip_number(self):
        return {
            "schema": {
                "type": "string",
                "empty": False,
            },
            "required": True,
            "excludes": "parcels_numbers",
        }

    def _parcels_numbers(self):
        return {
            "type": "list",
            "schema": {
                "type": "string",
                "empty": False,
            },
            "empty": False,
            "required": True,
            "excludes": "packing_slip_number",
        }

    def _schemas(self):
        return {
            "packing_slip_number": self._packing_slip_number(),
            "parcels_numbers": self._parcels_numbers(),
            "auth": self._auth(),
        }


class ApiParcelDocument(BaseApi):
    # https://www.colissimo.entreprise.laposte.fr/sites/default/files/2021-11/DocTechnique-WS-Documents_FR.pdf
    def __init__(self, config_object):
        self.config = config_object
        self.current_action = config_object.current_action

    def _parcel_number(self):
        return {
            "schema": {
                "type": "string",
                "empty": False,
                "default": "",
            },
            "required": True,
        }

    def _document_id(self):
        return {
            "schema": {
                "type": "string",
                "empty": False,
                "default": "",
            },
            "required": True,
        }

    def _document_type(self):
        return {
            "schema": {
                "type": "string",
                "empty": False,
                "default": "",
            },
            "required": True,
        }

    def _document_path(self):
        return {
            "schema": {
                "type": "string",
                "empty": False,
                "default": "",
            },
            "required": True,
        }

    def _schemas(self):
        schema = {"auth": self._auth(), "service": {}}
        if self.current_action == "get_documents":
            schema["service"].update(
                {
                    "parcel_number": self._parcel_number(),
                }
            )
        elif self.current_action == "get_document":
            schema["service"].update(
                {
                    "parcel_number": self._parcel_number(),
                    "document_id": self._document_id(),
                }
            )
        elif self.current_action in ("create_document", "update_document"):
            schema["service"].update(
                {
                    "parcel_number": self._parcel_number(),
                    "document_type": self._document_type(),
                    "document_path": self._document_path(),
                }
            )
        return schema
