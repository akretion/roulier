"""Implement for kuehne nagel."""
from roulier.transport import TransportBase
from jinja2 import Environment, PackageLoader
from collections import OrderedDict
from io import BytesIO

import logging

log = logging.getLogger(__name__)


class KuehneNagelFrTransportLabel(TransportBase):
    """Generate ZPL label """

    STATUS_SUCCESS = "Success"

    def send(self, body):
        """Call this function.
        Args:
            body: an object with a lot usefull values
        Return:
            {
                status: STATUS_SUCCES or STATUS_ERROR, (string)
                message: more info about status of result (None)
                response: (None)
                payload: usefull payload (if success) (body as string)
            }
        """
        parcels = body.pop("parcels", [])
        body["service"]["mhuQuantity"] = len(parcels)
        body["service"]["volume"] = sum(
            [parcel.get("volume", 0.0) for parcel in parcels]
        )
        body["service"]["weight"] = sum(
            [parcel.get("weight", 0.0) for parcel in parcels]
        )
        payload = {
            "labels": [],
            "trackingNumber": body["service"]["shippingName"],
        }
        for i, parcel in enumerate(parcels, 1):
            parcel["number"] = i
            body["parcel"] = parcel
            payload["labels"].append(
                {
                    "zpl": self.render_template(body, "kuehnenagel_generateLabel.zpl"),
                    "number": i,
                    "ref": body["parcel"]["reference"],
                }
            )
        if body["service"].get("customerId"):
            payload["trackingUrl"] = (
                "https://espace-services.kuehne-nagel-road.fr/redirect.aspx?IdExpediteur=%s&RefExpediteur=%s"
                % (body["service"]["customerId"], body["service"]["shippingName"])
            )
        return {
            "status": self.STATUS_SUCCESS,
            "message": None,
            "response": None,
            "payload": payload,
        }

    def render_template(self, body, template_name):
        env = Environment(
            loader=PackageLoader("roulier", "carriers/kuehne_nagel_fr/templates"),
        )
        template = env.get_template(template_name)
        return template.render(
            auth=body["auth"],
            service=body["service"],
            parcel=body["parcel"],
            sender_address=body["from_address"],
            recipient_address=body["to_address"],
        )
