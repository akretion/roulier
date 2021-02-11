""" API implementation for GLS """

from roulier.api import ApiParcel


class GlsApiParcel(ApiParcel):
    def _auth(self):
        schema = super(GlsApiParcel, self)._auth()
        # contact_id
        schema["login"].update({"required": True, "empty": False, "maxlength": 10})
        return schema

    def _service(self):
        schema = super(GlsApiParcel, self)._service()
        # {"shippingId": ""}
        schema["customerId"] = {"maxlength": 10, "minlength": 10, "required": True}
        # warehouse
        schema["agencyId"] = {"maxlength": 6, "minlength": 6, "required": True}
        schema["product"] = {"default": "France", "required": True}
        schema["reference2"] = {"maxlength": 20}
        schema["instructions"] = {"maxlength": 35}
        schema["consignee_ref"] = {"maxlength": 20}
        schema["parcel_total_number"] = {
            "max": 999,
            "type": "integer",
            "required": True,
        }
        return schema

    def _address(self):
        schema = super(GlsApiParcel, self)._address()
        schema["street1"].update({"maxlength": 35})
        schema["street2"] = {"maxlength": 35}
        schema["street3"] = {"maxlength": 35}
        schema["zip"].update({"maxlength": 10})
        schema["city"].update({"maxlength": 35})
        return schema

    def _from_address(self):
        schema = super(GlsApiParcel, self)._from_address()
        return schema

    def _to_address(self):
        schema = super(GlsApiParcel, self)._to_address()
        schema["company"].update({"maxlength": 35, "required": True})
        schema["contact"] = {"maxlength": 35}
        schema["consignee_phone"] = {"maxlength": 20}
        schema["consignee_mobile"] = {"maxlength": 20}
        schema["consignee_email"] = {"maxlength": 100}
        # for uniship label only
        schema["country"].update({"minlength": 2, "maxlength": 2, "type": "string"})
        schema["country_norme3166"] = {"max": 999, "min": 1, "type": "integer"}
        return schema

    def _parcel(self):
        schema = super(GlsApiParcel, self)._parcel()
        schema["parcel_number_label"] = {
            "max": 999,
            "type": "integer",
            "required": True,
        }
        schema["parcel_number_barcode"] = {
            "max": 999,
            "type": "integer",
            "required": True,
        }
        # TODO validate a weight of XX.XX (5 chars)  {0:05.2f}
        schema["weight"] = {"maxlength": 5, "required": True}
        schema["custom_sequence"] = {"maxlength": 10, "minlength": 10, "required": True}
        return schema


# def gls_countries_prefix():
#    """ Get prefix from pycountry lib
#    """
#    gls_prefix = []
#    for elm in pycountry.countries:
#        gls_prefix.append(str(elm.alpha_2))
#    # For GLS carrier 'Serbie Montenegro' is 'CS'
#    # and for wikipedia it's 'ME'
#    gls_prefix[gls_prefix.index('ME')] = 'CS'
#    return gls_prefix
