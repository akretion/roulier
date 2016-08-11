# -*- coding: utf-8 -*-
"""Transform input to laposte compatible xml."""
from jinja2 import Environment, PackageLoader
from roulier.codec import Encoder

LAPOSTE_ACTIONS = ('generateLabelRequest', 'getProductInter')
LAPOSTE_LABEL_FORMAT = (
    'ZPL_10x15_203dpi',
    'ZPL_10x15_300dpi',
    'DPL_10x15_203dpi',
    'DPL_10x15_300dpi',
    'PDF_10x15_300dpi',
    'PDF_A4_300dpi')


class LaposteEncoder(Encoder):
    """Transform input to laposte compatible xml."""

    def encode(self, api_input, action):
        """Transform input to laposte compatible xml."""
        if not (action in LAPOSTE_ACTIONS):
            raise Exception(
                'action %s not in %s' % (action, ', '.join(LAPOSTE_ACTIONS)))

        dj = self.api()
        dj['service'].update(api_input.get('service', {}) or {})
        dj['parcel'].update(api_input.get('parcel', {}) or {})
        dj['from_address'].update(api_input.get('from_address', {}) or {})
        dj['to_address'].update(api_input.get('to_address', {}) or {})
        dj['infos'].update(api_input.get('infos', {}) or {})
        # because customs.articles is an array, it needs a special treatment

        # todo refactor this
        input_customs = api_input.get('customs')
        if input_customs:
            dj['customs']['category'] = input_customs['category']
            dj['customs']['articles'] = []  # clean reset
            for article in input_customs['articles']:
                empty_article = self.api()['customs']['articles'][0]
                empty_article.update(article)
                dj['customs']['articles'].append(empty_article)

        service = {
            "productCode": dj['service']['productCode'],
            "depositDate": dj['service']['shippingDate'],
            "mailBoxPicking": "",
            "transportationAmount": dj['service']['transportationAmount'],
            "totalAmount": dj['service']['totalAmount'],
            "orderNumber": "",
            "commercialName": "",
            "returnTypeChoice": dj['service']['returnTypeChoice'],
        }

        output_format = {
            "x": 0,
            "y": 0,
            "outputPrintingType": self.lookup_label_format(
                dj['service']['labelFormat'])
        }

        parcel = {
            "weight": dj['parcel']['weight'],
            "nonMachinable": dj['parcel']['nonMachinable'],
            "instructions": dj['parcel']['instructions'],
            "pickupLocationId": dj['parcel']['pickupLocationId'],
            "insuranceValue": dj['parcel']['insuranceValue'],
            "recommendationLevel": dj['parcel']['recommendationLevel'],
            "cod": dj['parcel']['cod'],
            "codAmount": dj['parcel']['codAmount'],
            "ftd": dj['parcel']['ftd']
        }

        sender_address = {
            "companyName": dj['from_address']['company'],
            "lastName": dj['from_address']['name'],
            "firstName": dj['from_address']['firstname'],
            "line0": "",
            "line1": dj['from_address']['street1'],
            "line2": dj['from_address']['street2'],
            "line3": "",
            "countryCode": dj['from_address']['country'],
            "city": dj['from_address']['city'],
            "zipCode": dj['from_address']['zip'],
            "phoneNumber": dj['from_address']['phone'],
            "mobileNumber": "",
            "doorCode1": "",
            "doorCode2": "",
            "email": dj['from_address']['email'],
            "intercom": "",
            "language": "FR",
        }

        receiver_address = {
            "companyName": dj['to_address']['company'],
            "lastName": dj['to_address']['name'],
            "firstName": dj['to_address']['firstname'],
            "line0": "",
            "line1": dj['to_address']['street1'],
            "line2": dj['to_address']['street2'],
            "line3": "",
            "countryCode": dj['to_address']['country'],
            "city": dj['to_address']['city'],
            "zipCode": dj['to_address']['zip'],
            "phoneNumber": dj['to_address']['phone'],
            "phoneNumber": "",
            "mobileNumber": "",
            "doorCode1": "",
            "doorCode2": "",
            "email": dj['to_address']['email'],
            "intercom": dj['to_address']['intercom'],
            "language": "FR",
        }

        auth = {
            "contractNumber": dj['infos']['contractNumber'],
            "password": dj['infos']['password'],
        }

        customs = dj['customs']

        env = Environment(
            loader=PackageLoader('roulier', '/carriers/laposte/templates'),
            extensions=['jinja2.ext.with_'])

        template = env.get_template("laposte_%s.xml" % action)
        return template.render(
            auth=auth,
            service=service,
            outputFormat=output_format,
            parcel=parcel,
            sender_address=sender_address,
            receiver_address=receiver_address,
            customs=customs)

    def api(self):
        """Return API we are expecting."""
        address = {
            'company': "",
            'name': "",
            'street1': "",
            'street2': "",
            'country': "",
            'city': "",
            'zip': "",
            'phone': "",
            'email': "",
            "intercom": "",
        }

        return {
            "service": {
                'productCode': '',
                'shippingDate': '',
                'labelFormat': '',
                'transportationAmount': '',
                'totalAmount': '',
                'returnTypeChoice': '',
            },
            "parcel": {
                "weight": "",
                "nonMachinable": "",
                "instructions": "",
                "pickupLocationId": "",
                "insuranceValue": "",
                "recommendationLevel": "",
                "cod": "",
                "codAmount": "",
                "ftd": "",
            },
            "to_address": address.copy(),
            "from_address": address.copy(),
            "infos": {
                'contractNumber': '',
                'password': ''
            },
            "customs": {
                "articles": [{
                    "quantity": "",
                    "weight": "",
                    "description": "",
                    "hs": "",
                    "value": "",
                    "originCountry": "",
                }],
                "category": "",
            }
        }

    def lookup_label_format(self, label_format="ZPL"):
        """Get a Laposte compatible format of label.

        args:
            label_format: (str) ZPL or ZPL_10x15_300dpi
        return
            a value taken in LAPOSTE_LABEL_FORMAT
        """
        lookup = {
            'ZPL': 'ZPL_10x15_300dpi',
            'DPL': 'DPL_10x15_300dpi',
            'PDF': 'PDF_10x15_300dpi',
        }
        if label_format in LAPOSTE_LABEL_FORMAT:
            return label_format
        return lookup.get(label_format, 'PDF_10x15_300dpi')
