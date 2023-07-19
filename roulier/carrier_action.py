"""Abstract classes for different Carrier actions"""
from abc import ABC, abstractmethod


class CarrierBase(ABC):
    def __init__(self, carrier_type, action, **kwargs):
        self.carrier_type = carrier_type
        self.action = action


class CarrierWebservice(CarrierBase, ABC):

    is_test = False
    ws_test_url = ""
    roulier_input = None

    @property
    @abstractmethod
    def ws_url(self):
        pass

    @property
    @abstractmethod
    def transport(self):
        pass

    @property
    @abstractmethod
    def encoder(self):
        pass

    @property
    @abstractmethod
    def decoder(self):
        pass

    @property
    @abstractmethod
    def api(self):
        pass

    def _get_data_from_webservice(self, data):
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)
        self.roulier_input = data

        payload = encoder.encode(data)
        response = transport.send(payload)
        decoder.decode(response, payload)
        return decoder.result


class CarrierGetLabel(CarrierWebservice, ABC):
    @property
    @abstractmethod
    def manage_multi_label(self):
        """
        True if carrier webservice accept multiple parcels in one call or False
        if we have to make one call per parcels, even if it belongs to a same shipment
        """
        pass

    def get_label(self, carrier_type, action, data):
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)
        self.roulier_input = data

        parcels = data.get("parcels", []).copy()
        # one call to carrier webservice is enough
        if self.manage_multi_label or len(parcels) == 1:
            payload = encoder.encode(data)
            response = transport.send(payload)
            decoder.decode(response, payload)
        # one call by parcel
        else:
            for parcel in parcels:
                data["parcels"] = [parcel]
                payload = encoder.encode(data)
                response = transport.send(payload)
                decoder.decode(response, payload)
        return decoder.result


class CarrierGetPackingSlip(CarrierWebservice, ABC):
    """
    Manages the "packing slip" to give to the carrier who should sign it before taking
    the packages he will deliver
    """

    def get_packing_slip(self, carrier_type, action, data):
        """
        Retrieves the packing slip if the webservice handles it.
        If the webservice does not handle packing slip, we can generate out own printable html
        packing slip to give to the carrier.
        """
        return self._get_data_from_webservice(data)


class CarrierAddressValidation(CarrierWebservice, ABC):
    """
    Check if address is valid/known from the carrier and eventually get proposal
    if addresses that could match the input
    """

    def validate_address(self, carrier_type, action, data):
        return self._get_data_from_webservice(data)


class CarrierGetEdi(CarrierBase, ABC):
    """
    Generate an EDI file.
    """

    @property
    @abstractmethod
    def transport(self):
        pass

    @property
    @abstractmethod
    def encoder(self):
        pass

    @property
    @abstractmethod
    def api(self):
        pass

    def get_edi(self, carrier_type, action, data):
        """
        Generate EDI file
        """
        encoder = self.encoder(self)
        transport = self.transport(self)
        self.roulier_input = data

        payload = encoder.encode(data)
        return transport.send(payload)


class CarrierParcelDocument(CarrierWebservice, ABC):
    """
    Retrieve (or generate) a document for a specific parcel
    """

    is_test = False
    roulier_input = None
    current_action = None

    def _action(self, current_action, carrier_type, action, data):
        self.current_action = current_action
        encoder = self.encoder(self)
        decoder = self.decoder(self)
        transport = self.transport(self)
        self.roulier_input = data
        payload = encoder.encode(data)
        response = transport.send(payload)
        decoder.decode(response, payload)
        return decoder.result

    def get_documents(self, carrier_type, action, data):
        return self._action("get_documents", carrier_type, action, data)

    def get_document(self, carrier_type, action, data):
        return self._action("get_document", carrier_type, action, data)

    def create_document(self, carrier_type, action, data):
        return self._action("create_document", carrier_type, action, data)

    def update_document(self, carrier_type, action, data):
        return self._action("update_document", carrier_type, action, data)
