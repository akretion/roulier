# -*- coding: utf-8 -*-
"""Transform input to dpd compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder
from datetime import datetime
from .dpd_common import DPD_INFOS
from roulier.exception import InvalidApiInput
import logging
import copy
log = logging.getLogger(__name__)


class DpdEncoder(Encoder):
    """Transform input to dpd compatible xml."""

    def _fix_weight_type(self, api, data):
        """Because of hard to reproduce bug in cerberus
        some times the parcel's weight (dict in a list) is
        not validated correctly and leads to "must be of float type" error
        Cerberus 2.x will be out soon and I hope it will solve this issue.
        """
        out = copy.deepcopy(data)
        parcels = []
        parcel_schema = api._parcel()
        parcel_schema['weight']['coerce'] = float
        validator = api._validator()
        validator.schema = parcel_schema
        for parcel in out['parcels']:
            parcels.append(validator.normalized(parcel))
        out['parcels'] = parcels
        return out

    def encode(self, api_input, action):
        """Transform input to dpd compatible xml."""
        if not (action in DPD_INFOS):
            raise InvalidApiInput(
                'action %s not in %s' % (action, ', '.join(DPD_INFOS.keys())))
        api = DPD_INFOS[action]['api']()

        api_input2 = self._fix_weight_type(api, api_input)

        if not api.validate(api_input2):
            raise InvalidApiInput(
                'Input error : %s' % api.errors(api_input2))
        
        api_input2['service']['shippingDate'] = (
            datetime
            .strptime(api_input2['service']['shippingDate'], '%Y/%M/%d')
            .strftime('%Y%M%d')
        )
        data = api.normalize(api_input2)
       
        infos = {
            'url': "%s%s" % (
                DPD_INFOS[action]['endpoint'],
                DPD_INFOS[action]['service'],
            ),
            'service': DPD_INFOS[action]['service'],
            'action': action,
        }

        return {
            'auth': data['auth'],
            'body': data['body'],
            'infos': infos,
        }

    def api(self, action):
        api = DPD_INFOS[action]['api']()
        return api.api_values()