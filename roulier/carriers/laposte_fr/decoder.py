"""Laposte XML -> Python."""
from datetime import datetime
from lxml import objectify

from ...codec import DecoderGetLabel
from ...codec import DecoderGetPackingSlip
from ...codec import DecoderParcelDocument
import base64


class _UNSPECIFIED:
    pass


def _get_text(xml, tag, default=_UNSPECIFIED):
    """
    Returns the text content of a tag to avoid returning an lxml instance
    If no default is specified, it will raises the original exception of accessing
    to an inexistant tag
    """
    if not hasattr(xml, tag):
        if default is _UNSPECIFIED:
            # raise classic attr error
            return getattr(xml, tag)
        return default
    return getattr(xml, tag).text


def _get_cid(tag, tree):
    element = tree.find(tag)
    if element is None:
        return None
    href = element.getchildren()[0].attrib["href"]
    # href contains cid:236212...-38932@cfx.apache.org
    return href[len("cid:") :]  # remove prefix


class LaposteFrDecoderGetLabel(DecoderGetLabel):
    """Laposte XML -> Python."""

    def decode(self, response, input_payload):
        """Laposte XML -> Python."""
        body = response["body"]
        parts = response["parts"]
        output_format = input_payload["output_format"]

        xml = objectify.fromstring(body)
        msg = xml.xpath("//return")[0]

        rep = msg.labelV2Response
        cn23_cid = _get_cid("cn23", rep)
        label_cid = _get_cid("label", rep)

        annexes = []

        if cn23_cid:
            data = parts.get(cn23_cid)
            annexes.append(
                {"name": "cn23", "data": base64.b64encode(data), "type": "pdf"}
            )

        if rep.find("pdfUrl"):
            annexes.append({"name": "label", "data": rep.find("pdfUrl"), "type": "url"})
        parcel = {
            "id": 1,  # no multi parcel management for now.
            "reference": self._get_parcel_number(input_payload),
            "tracking": {
                # we need to force to real string because of those data can be reused
                # and cerberus won't accept an ElementString insteadof a string.
                "number": _get_text(rep, "parcelNumber"),
                "url": "",
                "partner": _get_text(rep, "parcelNumberPartner", ""),
            },
            "label": {
                "data": base64.b64encode(parts.get(label_cid)),
                "name": "label_1",
                "type": output_format,
            },
        }
        if hasattr(rep, "fields") and hasattr(rep.fields, "field"):
            for field in rep.fields.field:
                parcel["tracking"][_get_text(field, "key")] = _get_text(field, "value")
        self.result["parcels"].append(parcel)
        self.result["annexes"] += annexes


class LaposteFrDecoderGetPackingSlip(DecoderGetPackingSlip):
    """Laposte Bordereau Response XML -> Python."""

    def decode(self, response, input_payload):
        body = response["body"]
        parts = response["parts"]
        xml = objectify.fromstring(body)
        msg = xml.xpath("//return")[0]
        header = msg.bordereau.bordereauHeader
        published_dt = _get_text(header, "publishingDate", None)
        if published_dt:
            if "." in published_dt:
                # get packing slip with it's number does not return microseconds
                # but when creating a new one, it does... We remove microseconds in result
                # to have a better homogeneity
                published_dt = published_dt.split(".")
                published_dt = "%s+%s" % (
                    published_dt[0],
                    published_dt[1].split("+")[1],
                )
            published_datetime = datetime.strptime(published_dt, "%Y-%m-%dT%H:%M:%S%z")
        self.result["packing_slip"] = {
            "number": _get_text(header, "bordereauNumber", None),
            "published_datetime": published_datetime,
            "number_of_parcels": int(_get_text(header, "numberOfParcels", 0)),
            "site_pch": {
                "code": _get_text(header, "codeSitePCH", None),
                "name": _get_text(header, "nameSitePCH", None),
            },
            "client": {
                "number": _get_text(header, "clientNumber", None),
                "adress": _get_text(header, "Address", None),
                "company": _get_text(header, "Company", None),
            },
        }
        packing_slip_cid = _get_cid("bordereauDataHandler", msg.bordereau)
        if packing_slip_cid:
            self.result["annexes"].append(
                {
                    "name": "packing_slip",
                    "data": base64.b64encode(parts.get(packing_slip_cid)),
                    "type": "pdf",
                }
            )
        return self.result


class LaposteFrDecoderParcelDocument(DecoderParcelDocument):
    """Laposte Document Response JSON -> Python."""

    def decode(self, response, input_payload):
        error_code = response.get("errorCode") or "000"
        error_label = response.get("errorLabel") or ""
        if error_code != "000":
            self.result = None
            return self.result
        self.result = getattr(self, "_decode_%s" % self.current_action)(
            response, input_payload
        )
        return self.result

    def _decode_get_document(self, response, input_payload):
        return {"file": response["body"]}

    def _decode_get_documents(self, response, input_payload):
        return {d["uuid"]: {**d} for d in response["body"]["documents"]}

    def _decode_create_document(self, response, input_payload):
        return response["body"]["documentId"]

    def _decode_update_document(self, response, input_payload):
        return response["body"]["documentId"]
