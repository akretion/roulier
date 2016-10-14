# -*- coding: utf-8 -*-
"""API interface."""
from cerberus import Validator


class MyValidator(Validator):
    """Custom validator."""

    def _validate_description(self, description, field, value):
        """Allow 'description' in schema.

        The rule's arguments are validated against this schema:
        { 'description': 'a string'}
        """
        pass


class Api(object):
    """Define expected fields of carriers.

    This class should be overriden by each carrier.
    """

    def __init__(self):
        """."""
        v = MyValidator()
        v.allow_unknown = True
        v.purge_unknown = True
        self._validator = v

    def _address(self):
        return {
            'company': {'type': 'string', 'default': '', 'description': 'Company'},
            'name': {'type': 'string', 'default': '', 'required': True, 'empty': False},
            'street1': {'type': 'string', 'default': ''},
            'street2': {'type': 'string', 'default': ''},
            'country': {'type': 'string', 'default': '', 'description': 'ISO 3166-1 alpha-2 '},
            'city': {'type': 'string', 'default': ''},
            'zip': {'type': 'string', 'default': ''},
            'phone': {'type': 'string', 'default': '', 'description': 'Phone'},
            'email': {'type': 'string', 'default': ''},
        }

    def _from_address(self):
        address = self._address()
        return address

    def _to_address(self):
        address = self._address()
        address['street1'].update({'required': True, 'empty': False})
        address['country'].update({'required': True, 'empty': False})
        address['city'].update({'required': True, 'empty': False})
        address['zip'].update({'required': True, 'empty': False})
        return address

    def _parcel(self):
        return {
            "weight": {'type': 'float', 'default': '', 'description': 'Weight in kg', 'required': True, 'empty': False},
        }

    def _service(self):
        return {
            "product": {'default': '', 'description': ''},
            "agencyId": {'default': '', 'description': ''},
            "customerId": {'default': '', 'description': ''},
            "shippingId": {'default': ''},
            'shippingDate': {'default': '', 'type': 'string', 'required': True, 'empty': False, 'description': 'When the carrier has the package. Format: YYYY/MM/DD'},
            'reference1': {'type': 'string', 'default': '', 'description': 'Additionnal info visible by the client. Example : order number'},
            'reference2': {'type': 'string', 'default': ''},
            'reference3': {'type': 'string', 'default': ''},
            "labelFormat": {'description': 'Format of output (usually pdf or zpl)', 'default': ''},
            "instructions": {'description': 'Additionnal instructions for delivery', 'default': ''},
        }

    def _auth(self):
        return {
            'login': {'type': 'string', 'default': ''},
            'password': {'type': 'string', 'default': ''},
        }

    def _schemas(self):
        return {
            'service': self._service(),
            'auth': self._auth(),
            'parcel': self._parcel(),
            'from_address': self._from_address(),
            'to_address': self._to_address(),
        }

    def api_schema(self):
        """Return the expected schema of the api.

        A validation schema is a mapping, usually a dict.
        Schema keys are the keys allowed in the target dictionary.
        Schema values express the rules that must be matched
        by the corresponding target values.

        See http://docs.python-cerberus.org/en/stable/schemas.html

        """
        v = MyValidator()
        schemas = self._schemas()

        return {
            s: {
                'schema': schemas[s],
                'default': v.normalized({}, schemas[s])
            }
            for s in schemas}

    def api_values(self):
        """Return a dict containing expected keys.

        It's a normalized version of the schema.
        """
        return self.normalize({})

    def errors(self, data):
        """Return validation errors."""
        self._validator.validate(data, self.api_schema())
        return self._validator.errors

    def validate(self, data):
        """Ensure the data are valid.

        returns: bool

        See also errors()
        """
        return self._validator.validate(data, self.api_schema())

    def normalize(self, data):
        """Retrurn a normalized dict based on input.

        See http://docs.python-cerberus.org/en/stable/usage.html
        """
        return self._validator.normalized(data, self.api_schema())
