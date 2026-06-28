"""Mondial Relay Connect XML response -> roulier standard output."""

import logging

from lxml import etree

from roulier.codec import DecoderGetLabel
from roulier.exception import CarrierError

log = logging.getLogger(__name__)


class MondialRelayConnectDecoder(DecoderGetLabel):
    def decode(self, response, payload):
        output_type = payload.get("output_type", "PdfUrl")
        root = self._parse(response["body"])

        errors, warnings = self._read_statuses(root)
        for warning in warnings:
            log.warning("Mondial Relay Connect: %s", warning.get("message"))
        if errors:
            raise CarrierError(response.get("response"), errors)

        shipment_number = self._read_shipment_number(root)
        label_output = self._read_output(root)
        barcodes = self._read_barcodes(root)

        if not label_output and not barcodes:
            raise CarrierError(
                response.get("response"),
                [{"id": None, "message": "No label returned by Mondial Relay Connect"}],
            )

        reference = self._get_parcel_number(payload)
        self.result["parcels"] += self._build_parcels(
            shipment_number, barcodes, label_output, output_type, reference
        )

    def _build_parcels(
        self, shipment_number, barcodes, label_output, output_type, reference
    ):
        label = None
        if label_output:
            # Match the roulier convention (e.g. laposte): label data is bytes.
            # For ZplCode / IplCode the Connect API already returns base64 content,
            # so the consumer base64-decodes it to get the raw ZPL/IPL; for PdfUrl
            # it is a URL. The carrier output is exposed as bytes either way.
            label = {
                "data": label_output.encode("utf-8"),
                "name": "label_1",
                "type": output_type,
            }

        if not barcodes:
            parcel = {
                "id": shipment_number or "",
                "reference": reference,
                "tracking": {
                    "number": shipment_number or "",
                    "url": "",
                    "partner": "",
                },
            }
            if label:
                parcel["label"] = label
            return [parcel]

        parcels = []
        for index, barcode in enumerate(barcodes):
            parcel = {
                "id": barcode,
                "reference": reference,
                "tracking": {"number": barcode, "url": "", "partner": ""},
            }
            # The Connect API returns a single label stream for the shipment:
            # attach it to the first parcel.
            if index == 0 and label:
                parcel["label"] = label
            parcels.append(parcel)
        return parcels

    @staticmethod
    def _parse(raw):
        """Parse the response bytes, tolerating a UTF-16 declaration."""
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        head = raw[:200].lower()
        if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or b'encoding="utf-16"' in head:
            text = raw.decode("utf-16")
        else:
            text = raw.decode("utf-8", errors="replace")
        # Drop the declaration so lxml does not complain about the encoding of a
        # str, then parse.
        text = text.lstrip("﻿")
        parser = etree.XMLParser(recover=True, resolve_entities=False)
        return etree.fromstring(text.encode("utf-8"), parser=parser)

    def _read_statuses(self, root):
        errors = []
        warnings = []
        for status in root.xpath("//*[local-name()='Status']"):
            code = self._field(status, "code")
            level = self._field(status, "level").lower()
            message = self._field(status, "message")
            entry = {"id": code or None, "message": message, "level": level}
            if "error" in level:
                errors.append(entry)
            elif "warn" in level:
                warnings.append(entry)
            # Success / info statuses are ignored.
        return errors, warnings

    @staticmethod
    def _read_shipment_number(root):
        nodes = root.xpath("//*[local-name()='Shipment']")
        for node in nodes:
            number = node.get("ShipmentNumber")
            if number:
                return number
        return None

    @staticmethod
    def _read_output(root):
        nodes = root.xpath("//*[local-name()='Output']")
        if nodes and nodes[0].text:
            return nodes[0].text.strip()
        return None

    @staticmethod
    def _read_barcodes(root):
        barcodes = []
        for node in root.xpath("//*[local-name()='Barcode']"):
            value = node.get("Value") or (node.text or "").strip()
            if value:
                barcodes.append(value)
        return barcodes

    @staticmethod
    def _field(node, name):
        """Read a status field as an attribute or a child, case-insensitively."""
        for attr, value in node.attrib.items():
            if attr.lower() == name:
                return value.strip()
        for child in node:
            tag = etree.QName(child).localname.lower()
            if tag == name and child.text:
                return child.text.strip()
        return ""
