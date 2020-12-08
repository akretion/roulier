"""Factory of main classes."""


class RoulierFactory(object):
    def __init__(self):
        self._carrier_action = {}

    def register_builder(self, carrier_type, action, Carrierclass):
        self._carrier_action[(carrier_type, action)] = Carrierclass

    def get(self, carrier_type, action, **kwargs):
        carrierclass = self._carrier_action.get((carrier_type, action))
        if not carrierclass:
            raise ValueError((carrier_type, action))
        return carrierclass(carrier_type, action, **kwargs)


factory = RoulierFactory()


# generic method which call the right action on the right class.
def get(carrier_type, action, *args, **kwargs):
    carrier_obj = factory.get(carrier_type, action)
    return getattr(carrier_obj, action)(carrier_type, action, *args, **kwargs)


def get_carriers_action_available():
    """
    Return all possible action by implemented carriers.
    """
    action_by_carrier = {}
    for carrier_type, action in factory._carrier_action.keys():
        if not carrier_type in action_by_carrier:
            action_by_carrier[carrier_type] = []
        action_by_carrier[carrier_type].append(action)
    return action_by_carrier
