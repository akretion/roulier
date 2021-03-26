"""Gls weird string -> Python"""

import base64
from io import BytesIO
import logging
import os
import re
from string import Template

from roulier.codec import DecoderGetLabel
from roulier.exception import CarrierError

from .encoder import merge_dict

log = logging.getLogger(__name__)

ZPL_FILE_PATH = os.path.join(os.path.dirname(__file__), "templates/zpl.zpl")


class GlsDecoder(DecoderGetLabel):
    """Gls weird string -> Python."""

    def decode(self, response, input_payload):
        """Gls -> Python."""
        data = self.exotic_serialization_to_dict(response.get("body"))
        self.search_exception(data, input_payload)
        data_file = BytesIO(self.populate_label(data).encode())
        self.result["parcels"].append(
            {
                "id": 1,  # no multi parcel management for now.
                "reference": self._get_parcel_number(input_payload),
                "tracking": {"number": data.get("T8913"), "url": ""},
                "label": {
                    "data": base64.b64encode(data_file.read()),
                    "name": "label_%s" % data.get("T8913"),
                    "type": "zpl2",
                },
            }
        )

    def exotic_serialization_to_dict(self, data):
        res = {}
        # remove start of string
        data = re.sub(r"\\*GLS\\*", "", data)
        for val in data.split("|")[0:-1]:
            key, value = val.split(":", 1)
            res[key] = value
        return res

    def populate_label(self, data):
        with open(ZPL_FILE_PATH, "r") as f:
            zpl = f.read()
            unmatch_keys = self.validate_template(zpl, data.keys())
            key_with_empty_vals = {x: "" for x in unmatch_keys}
            data.update(key_with_empty_vals)
            t = Template(zpl)
            return t.substitute(data)

    def search_exception(self, data, data_request):
        exception, value = "", ""
        result = data.get("RESULT")
        components = result.split(":")
        code, tag = components[0], components[1]
        if len(components) == 3:
            # Not sure we always have 3 components
            value = components[2]
        if code == "E000":
            return False
        ctx_except = "Web service error : code: %s ; tag: %s ; value: %s" % (
            code,
            tag,
            value,
        )
        if code == "E999":
            exception = (
                "Unibox server (web service) is not responding.\n"
                "Check network connection, webservice accessibility."
            )
        elif tag == "T330":
            zip_code = ""
            if data["T330"]:
                zip_code = data["T330"]
            exception = (
                "Postal code '%s' is wrong (relative to the "
                "destination country)" % zip_code
            )
        elif tag == "T100":
            cnty_code = ""
            if data["T100"]:
                cnty_code = data["T100"]
            exception = "Country code '%s' is wrong" % cnty_code
        else:
            info = {}
            merge_dict(info)
            log.warning("Exception according these data:")
            detail = """Tag "%s" (%s), value %s""" % (tag, info.get(tag), value)
            log.warning(detail)
            exception = "wrong or absent information : %s" % detail
        if exception:
            self.create_exception(result, exception, ctx_except, data_request)
        return False

    def create_exception(self, result, exception, ctx_except, data_request):
        exc = "%s\n\n" "Contexte :\n\t%s" % (exception, ctx_except)
        log.warning("Gls exception Roulier library ")
        log.warning(exc)
        log.warning("Données envoyées:\n%s" % data_request)
        raise CarrierError(result, exc)

    def validate_template(self, template_string, available_keys):
        keys2match = []
        for match in re.findall(r"\$\{(T[0-9].*)\}", template_string):
            keys2match.append(match)
        unmatch = list(set(keys2match) - set(available_keys))
        not_in_tmpl_but_known_case = ["T8900", "T8901", "T8717", "T8911"]
        unknown_unmatch = list(unmatch)
        for elm in not_in_tmpl_but_known_case:
            if elm in unknown_unmatch:
                unknown_unmatch.remove(elm)
        if len(unknown_unmatch) > 0:
            log.info(
                "GLS carrier : these keys \n%s\nare defined "
                "in template but without valid replacement "
                "values\n" % unknown_unmatch
            )
        return unmatch
