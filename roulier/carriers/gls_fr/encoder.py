"""Transform input to gls compatible format"""

import logging
from datetime import date

from roulier.codec import Encoder
from roulier.exception import InvalidApiInput
from .api import GlsApi


GLS_ACTIONS = ('label',)

_logger = logging.getLogger(__name__)


DELIVERY_MAPPING = {
    # 'address': ADDRESS_MODEL,
    'T859': "consignee_ref",
    'T854': "reference1",  # additional_ref
    'T8907': "reference1",
    'T8908': "reference2",
    'T540': "shippingDate",
    'T8318': "instructions",  # commentary
    'T8975': "gls_origin_reference",
    'T8905': "parcel_total_number",
    'T8702': "parcel_total_number",
}
AUTH_MAPPING = {
    'T8915': "customerId",
    'T8914': "login",
    'T8700': "agencyId",  # outbound_depot
}
ACCOUNT_MAPPING = {
    # shipper
    'T820': "street1",
    'T810': "name",
    'T822': "zip",
    'T823': "city",
    'T821': "country",
}
ADDRESS_MAPPING = {
    'T860': "company",
    'T8906': "name",
    'T863': "street1",
    'T861': "street2",
    'T862': "street3",
    'T330': "zip",
    'T864': "city",
    'T100': "country_code",
    'T871': "phone",
    'T1230': "mobile",
    'T1229': "email",
}

PARCEL_MAPPING = {
    'T530': "weight",
    'T8973': "parcel_number_barcode",
    'T8904': "parcel_number_label",
}


def merge_dict(mydict):
    mydict.update(AUTH_MAPPING)
    mydict.update(ACCOUNT_MAPPING)
    mydict.update(DELIVERY_MAPPING)
    mydict.update(PARCEL_MAPPING)


class GlsEncoder(Encoder):
    """Transform input to gls compatible format."""

    def encode(self, api_input, action='label'):
        """Transform input to gls compatible format."""
        if action != GLS_ACTIONS[0]:
            raise Exception(
                'action %s not in %s' % (action, ', '.join(GLS_ACTIONS)))
        api = GlsApi()
        # if not api.validate(api_input):
        #     _logger.warning('GLS api call exception:')
        #     # import pdb; pdb.set_trace()
        #     raise InvalidApiInput(
        #         {'api_call_exception': api.errors(api_input)})
        raw_data = api.normalize(api_input)
        data = self.merge_data(raw_data)
        data = self.dict_to_exotic_serialization(data)
        return {"isTest": raw_data.get('auth').get('isTest'), "data": data}

    def merge_data(self, raw_data):
        data, to_address, flat_dict = {}, {}, {}
        # addresses dict contains same keys, then we extract the first one
        for key, val in ADDRESS_MAPPING.items():
            to_address[key] = raw_data['to_address'].get(val)
        del raw_data['to_address']
        del raw_data['parcels']
        for key in raw_data:
            flat_dict.update(raw_data[key])
        data.update(to_address)
        merge_dict(data)
        for key, val in data.items():
            data[key] = flat_dict.get(val, data[key])
            if isinstance(data[key], date):
                data[key] = data[key].strftime("%Y%m%d")
        return data

    def dict_to_exotic_serialization(self, data):
        res = r'\\\\\GLS\\\\\|'
        for key, val in data.items():
            if val not in ('', False):
                res += "%s:%s|" % (key, val)
        res += r'/////GLS/////'
        print(res)
        return res

    def api(self):
        """Return API we are expecting."""
        return GlsApi().api_values()

    def lookup_label_format(self, label_format="ZPL"):
        """ Get a Gls compatible format of label.

        args:
            label_format: (str) ZPL or ZPL_10x15_300dpi
        return
            a value taken in GLS_LABEL_FORMAT
        """
