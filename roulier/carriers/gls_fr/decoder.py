"""Gls weird string -> Python"""

import logging
import os
from string import Template
from roulier.codec import Decoder
from roulier.exception import CarrierError
from .encoder import merge_dict

log = logging.getLogger(__name__)

ZPL_FILE_PATH = os.path.join(os.path.dirname(__file__), "templates/zpl.zpl")


class GlsDecoder(Decoder):
    """Gls weird string -> Python."""

    def decode(self, body):
        """Gls -> Python."""

        data = self.exotic_serialization_to_dict(body)
        self.raise_on_error(data)
        return {
            "tracking_number": data.get("T8913"),
            "content": self.populate_label(data),
            "name": data.get("T8913")
        }

    def exotic_serialization_to_dict(self, data):
        res = {}
        for val in data.split('|')[1:-1]:
            key, value = val.split(':', 1)
            res[key] = value
        return res

    def populate_label(self, data):
        with open(ZPL_FILE_PATH, 'r') as f:
            zpl = f.read()
            unmatch_keys = self.validate_template(zpl, data.keys())
            key_with_empty_vals = {x: '' for x in unmatch_keys}
            data.update(key_with_empty_vals)
            t = Template(zpl)
            return t.substitute(data)

    def raise_on_error(self, data):
        errors, value = [], ""
        result = data.get('RESULT')
        components = result.split(':')
        code, tag = components[0], components[1]
        if len(components) == 3:
            # Not sure we always have 3 components
            value = components[2]
        if code == 'E000':
            return False
        message = "Web service error : code: %s ; tag: %s ; value: %s"
        log.warning(message % (code, tag, value))
        if code == 'E999':
            log.warning(
                "Unibox server (web service) is not responding.\n"
                "Check network connection, webservice accessibility.")
        elif tag == 'T330':
            zip_code = ''
            if data['T330']:
                zip_code = data['T330']
            errors.append(
                "Postal code '%s' is wrong (relative to the "
                "destination country)" % zip_code)
        elif tag == 'T100':
            cnty_code = ''
            if data['T100']:
                cnty_code = data['T100']
            errors.append("Country code '%s' is wrong" % cnty_code)
        else:
            info = {}
            merge_dict(info)
            log.warning("""Tag "%s" (%s), value %s""" % (
                tag, info.get(tag), value))
        log.info("""
        >>> Rescue label will be printed instead of the standard label""")
        if len(errors) > 0:
            raise CarrierError(ResponseObject(result), errors[0])
        return False

    def validate_template(self, template_string, available_keys):
        import re
        keys2match = []
        for match in re.findall(r'\$(T[0-9].*) ', template_string):
            keys2match.append(match)
        unmatch = list(set(keys2match) - set(available_keys))
        not_in_tmpl_but_known_case = ['T8900', 'T8901', 'T8717', 'T8911']
        unknown_unmatch = list(unmatch)
        for elm in not_in_tmpl_but_known_case:
            if elm in unknown_unmatch:
                unknown_unmatch.remove(elm)
        if len(unknown_unmatch) > 0:
            log.info("GLS carrier : these keys \n%s\nare defined "
                     "in template but without valid replacement "
                     "values\n" % unknown_unmatch)
        return unmatch


class ResponseObject():
    """ Minimal response object for Roulier integration
    """
    text = None

    def __init__(self, text):
        self.text = text
