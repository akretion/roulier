from roulier.codec import Encoder


class KuehneNagelFrEncoder(Encoder):

    # dummy encoder since it is mandatory in the process but no needed for kuehne
    # since there is no call to webservice. Label is generated in the transport step
    def transform_input_to_carrier_webservice(self, data):
        return data
