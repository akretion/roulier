"""UPS response -> Python."""

from roulier.codec import DecoderGetLabel


class UpsDecoder(DecoderGetLabel):
    """UPS response -> Python."""

    def decode(self, response, input_payload):
        all_labels_data = (
            response.get("ShipmentResponse")
            .get("ShipmentResults")
            .get("PackageResults")
        )
        if isinstance(all_labels_data, dict):
            all_labels_data = [all_labels_data]
        i = 0
        for label_data in all_labels_data:
            self.result["parcels"].append(
                {
                    "id": i + 1,
                    "reference": self._get_ups_parcel_number(i),
                    "tracking": {
                        "number": label_data.get("TrackingNumber"),
                        "url": "",
                    },
                    "label": {  # same as main label
                        "name": label_data.get("TrackingNumber"),
                        "data": label_data.get("ShippingLabel").get("GraphicImage"),
                        "type": label_data.get("ShippingLabel")
                        .get("ImageFormat")
                        .get("Code")
                        .lower(),
                    },
                }
            )
            i += 1

    # In case of multi parces, there is way to find the reference of our package
    # in UPS response. The parcel reference sent to the UPS API is not part of the UPS
    # response AFAIK.
    # So we assume UPS the tracking and labels for the package in the same order
    # than we sent it.
    def _get_ups_parcel_number(self, package_index):
        roulier_input = self.config.roulier_input or {}
        parcels = roulier_input.get("parcels", [])
        parcel_ref = parcels[package_index].get("reference", "")
        return parcel_ref
