"""Implementation of Dpd Api."""

from roulier.api import ApiParcel
from roulier.api import MyValidator

DPD_LABEL_FORMAT = (
    "PDF",
    "PDF_A6",
    "PNG",
    "ZPL",
)

DPD_ALLOWED_NOTIFICATIONS = (
    "No",
    "Predict",
    "AutomaticSMS",
    "AutomaticMail",
)
DPD_PRODUCTS = (
    "DPD_Classic",
    "DPD_Relais",
    "DPD_Predict",
    # 'DPD Retour en Relais',  # Not implemented yet
)


class DpdValidator(MyValidator):
    def _validate_product(self, _, field, value):
        """
        Tests some complex constraints relate to the product type and other fields values

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        product = self.document.get("product")
        pickup_id = self.document.get("pickupLocationId", "").strip()
        notifications = self.document.get("notifications")
        if pickup_id and product in ("DPD_Predict", "DPD_Classic"):
            self._error(
                "pickupLocationId", "pickupLocationId can't be used with %s" % product
            )
        if product == "DPD_Predict":
            if notifications and notifications != "Predict":
                self._error(
                    "notifications", "must be set to Predict when using Predict"
                )
        else:
            if notifications == "Predict":
                self._error(
                    "notifications",
                    "Predict notifications can't be used with %s" % product,
                )
            if product == "DPD_Relais" and not pickup_id:
                self._error(
                    "pickupLocationId", "pickupLocationId is mandatory for Relais"
                )


class DpdApi(ApiParcel):
    def _validator(self):
        v = DpdValidator()
        v.allow_unknown = True
        # v.purge_unknown = True
        return v

    def _service(self):
        schema = super(DpdApi, self)._service()
        schema["labelFormat"]["allowed"] = DPD_LABEL_FORMAT
        schema["labelFormat"]["default"] = "ZPL"
        schema["labelFormat"].update({"required": True, "empty": False})
        schema["agencyId"].update(
            {
                "required": True,
                "empty": False,
                # 'description': 'Agency code int(3)'
            }
        )
        schema["customerCountry"] = {
            "required": True,
            "empty": False,
            # 'description': 'Customer country code (France = 250) int(3)'
        }
        schema["customerId"].update(
            {
                "required": True,
                "empty": False,
                # 'description': 'Customer number int(6)'
            }
        )
        schema["shippingDate"].update({"required": False, "empty": True})

        # mettre ça ensemble ?
        schema["notifications"] = {
            "default": DPD_ALLOWED_NOTIFICATIONS[0],
            "allowed": DPD_ALLOWED_NOTIFICATIONS,
        }
        schema["product"].update(
            {
                "empty": False,
                "required": True,
                "default": DPD_PRODUCTS[0],
                # 'description': 'Type de produit',
                "allowed": DPD_PRODUCTS,
                "product": True,
            }
        )

        schema["pickupLocationId"] = {
            "default": "",
            "empty": True,
            "required": False,
            # 'description': 'Drop-off Location id (Relais Colis)'
        }

        # Whether to use the legacy DPD API or the new GeoLabel compatible one
        schema["legacy"] = {
            "required": False,
            "default": False,
        }

        return schema

    def _address(self):
        schema = super(DpdApi, self)._address()
        # schema['street2']['description'] = (
        #     "N/A for DPD. It will be appended to street1")
        schema["country"].update({"required": True, "empty": False})
        schema["zip"].update({"required": True, "empty": False})
        schema["city"].update({"required": True, "empty": False})
        return schema

    def _to_address(self):
        schema = super(DpdApi, self)._to_address()
        # , 'description': """First name""",
        schema["firstName"] = {"default": "", "coerce": "accents"}
        schema["door1"] = {"default": ""}  # 'description': """Door code 1"""
        schema["door2"] = {"default": ""}  # 'description': """Door code 2"""}
        schema["intercom"] = {"default": ""}  # 'description': """Intercom"""}
        for field in ["city", "company", "name", "street1", "street2"]:
            schema[field].update({"coerce": "accents"})
        return schema

    def _from_address(self):
        schema = super(DpdApi, self)._from_address()
        schema["phone"].update({"required": True, "empty": False})
        return schema

    def _auth(self):
        schema = super(DpdApi, self)._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"]["required"] = False
        return schema
