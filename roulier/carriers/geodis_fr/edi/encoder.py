"""Implementation of Geodis Api."""
from datetime import datetime
from roulier.codec import Encoder


class GeodisFrEncoderEdi(Encoder):
    def transform_input_to_carrier_webservice(self, data):
        return {
            "body": self.encode_agency(
                agency_address=data["agency_address"],
                from_address=data["from_address"],
                shipments=data["shipments"],
                service=data["service"],
            ),
            "headers": data["service"],
        }

    def encode_shipment(self, shipment, service, idx):
        packs = shipment["parcels"]
        to_address = shipment["to_address"]
        # There is company notion in to_address, so if company exists
        # we put it in dest name and person name in contact name.
        # if it does not exist, we just put person name in both dest name
        # and contact name. Same is done in webservice side.
        dest_name = to_address.get("company") or to_address["name"]
        contact_name = to_address["name"]
        lines = [
            ["CNI", "%s" % idx, shipment["shippingId"]],
            [
                "TSR",
                "2",  # 4065
                [shipment["product"], "", "", shipment["productOption"]],  # 7273
                shipment["productPriority"],  # 4219
                shipment["notifications"],  # 7085 : M, S, P
            ],
            # /*MOA si envoi international */
            # ['MOA', '43', $shipment['cost'], 'EUR'],
            ["FTX", "DEL", "", "", shipment["reference2"]],
            ["TOD", "6", "PP", shipment["productTOD"]],
            ["RFF", ["ADE", service["customerId"]]],
            ["RFF", ["ACL", shipment["reference1"]]],
            [
                "NAD",
                "CN",
                "",
                "",  # C058
                dest_name,
                [to_address["street1"], to_address["street2"]],
                to_address["city"],
                "",  # 3164
                to_address["zip"],
                to_address["country"],
            ],
            ["CTA", "IC", ["", contact_name]],
        ]
        if to_address["email"]:
            lines.append(["COM", [to_address["email"], "EM"]])
        if to_address["phone"]:
            lines.append(["COM", [to_address["phone"], "TE"]])
        j = 0
        for pack in packs:
            j = j + 1
            lines += [
                ["GID", "%s" % j, ["1", "PC", "21", "6"]],
                ["MEA", "AAE", "AAD", ["KGM", "%s" % pack["weight"]]],
                ["PCI", "18"],
                ["GIN", "BN", pack["barcode"]],
            ]
        return lines

    def encode_agency(self, agency_address, from_address, shipments, service):
        shipment_lines = []
        i = 0
        deposit = service["depositId"]
        date = datetime.now()
        for shipment in shipments:
            i = i + 1
            shipment_lines += self.encode_shipment(shipment, service, i)

        lines = [
            ["UNH", deposit, ["IFCSUM", "D", "96A", "UN", "ETT021"]],
            ["BGM", "630", deposit],
            ["DTM", ["137", date.strftime("%Y%m%d%H%M"), "203"]],
            ["RFF", ["ADE", service["customerId"]]],
            ["TDT", "20", "", "30", "31"],
            [
                "NAD",
                "CA",
                [agency_address["siret"], "100"],
                "",  # C058
                agency_address["name"],
                [agency_address["street1"], agency_address["street2"]],
                agency_address["city"],
                "",  # 3164
                agency_address["zip"],
                agency_address["country"],
            ],
            [
                "NAD",
                "CZ",
                [from_address["siret"], "100"],
                "",  # C058
                from_address["name"],
                [from_address["street1"], from_address["street2"]],
                from_address["city"],
                "",  # 3164
                from_address["zip"],
                from_address["country"],
            ],
            ["DOC", "630", deposit],
        ] + shipment_lines
        lines += [["UNT", "%s" % (len(lines) + 1), deposit]]
        return lines
