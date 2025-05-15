# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from base64 import b64decode


def assert_data_type(b64_data, expected_type):
    data = b64decode(b64_data)
    if expected_type == "EPL":  # No magic bytes for EPL
        assert len(data) > 0, "EPL data should not be empty"
        assert b"\r\n" in data
        return

    magic_bytes = {
        "PDF": b"%PDF-",
        "PNG": b"\x89PNG\r\n",
        # https://gist.github.com/metafloor/773bc61480d1d05a976184d45099ef56
        "ZPL": b"^XA",
    }
    if expected_type not in magic_bytes:
        raise ValueError(f"Unsupported type: {expected_type}")

    if expected_type == "ZPL":
        if data[:3] == b"\xef\xbb\xbf":
            # Handle ZPL data that starts with the byte order mark (BOM)
            data = data[3:]
        if not data.startswith(magic_bytes[expected_type]) and b"\n" in data:
            # Try next line
            data = data.split(b"\n", 1)[1]

    assert data.startswith(magic_bytes[expected_type]), f"Invalid {expected_type} data"


def assert_pdf(b64_data):
    assert_data_type(b64_data, "PDF")


def assert_zpl(b64_data):
    assert_data_type(b64_data, "ZPL")
