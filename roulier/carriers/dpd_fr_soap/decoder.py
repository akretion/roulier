"""Dpd XML -> Python."""
import base64
from lxml import objectify

from roulier import ws_tools as tools
from roulier.codec import DecoderGetLabel


class DpdDecoder(DecoderGetLabel):
    """Dpd XML -> Python."""

    def decode(self, response, input_payload):
        """Understand a CreateShipmentWithLabelsResponse."""
        output_format = input_payload["output_format"]
        is_legacy = input_payload["is_legacy"]
        xml = objectify.fromstring(response["body"])

        shipments, files = getattr(
            xml, "CreateShipmentWithLabels%sResult" % ("" if is_legacy else "Bc")
        ).getchildren()

        if is_legacy:
            shipment = shipments.getchildren()[0]
            parcel_field = "parcelnumber"
            barcode_field = "barcode"
        else:
            shipmentbc = shipments.getchildren()[0]
            shipment = shipmentbc.getchildren()[0]
            parcel_field = "BarcodeId"
            barcode_field = "BarCode"

        annexes = []
        for dpdfile in files.getchildren():
            # label file : EPRINT legacy type, BIC3 geolabel type
            if dpdfile.type.text in ("EPRINT", "BIC3"):
                parcel = {
                    "id": 1,
                    "reference": self._get_parcel_number(input_payload)
                    or getattr(shipment, parcel_field).text,
                    "tracking": {
                        "number": getattr(shipment, barcode_field).text,
                        "url": "",
                        "partner": "",
                    },
                    "label": {  # same as main label
                        "data": dpdfile.label.text,
                        "name": "label 1",
                        "type": output_format,
                    },
                }
                self.result["parcels"].append(parcel)
            # summary file (EPRINTATTACHMENT) or any other file but not supported yet.
            else:
                self.result["annexes"].append(
                    {
                        "data": dpdfile.label.text,
                        "name": "Summary",
                        "type": output_format,
                    }
                )
