from roulier.api import ApiParcel


class KuehneNagelFrParcelApi(ApiParcel):
    def _service(self):
        schema = super()._service()
        schema.update(
            {
                "goodsName": {"default": ""},
                "epalQuantity": {"default": 0},
                "shippingOffice": {"required": True, "empty": False},
                "shippingRound": {"default": 0},
                "shippingName": {"required": True, "empty": False},
                "deliveryContract": {"default": "", "type": "string"},
                "labelDeliveryContract": {"default": "C", "type": "string"},
                "exportHub": {"default": ""},
                "orderName": {"default": ""},
                "shippingConfig": {"default": "P"},
                "vatConfig": {"default": "V"},
                "deliveryType": {"default": "D"},
                "serviceSystem": {"default": "3"},
                "note": {"default": ""},
                "kuehneOfficeName": {"required": True, "empty": False},
                "labelLogo": {"default": ""},
            }
        )
        return schema

    def _parcel(self):
        schema = super()._parcel()
        schema.update(
            {"weight": {"default": 0}, "volume": {"default": 0},}
        )
        return schema
