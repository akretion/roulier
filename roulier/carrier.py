# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from functools import wraps
import logging
import typing
from .roulier import factory
from .exception import CarrierError, InvalidApiInput


log = logging.getLogger(__name__)


class MetaCarrier(type):
    """
    Metaclass for Carrier classes.

    Used to register carrier actions in the roulier factory.
    """

    def __new__(cls, name, bases, dct):
        carrier = super().__new__(cls, name, bases, dct)

        if not hasattr(carrier, "__key__"):
            carrier.__key__ = carrier.__name__.lower()

        name = getattr(carrier, "__key__")

        for key, value in dct.items():
            if getattr(value, "__action__", False):
                log.debug(f"Registering {key} for {name}")
                factory.register_builder(name, key, carrier)

        return carrier


class Carrier(metaclass=MetaCarrier):
    """
    Base class for pydantic carriers.
    """

    def __init__(self, carrier_type, action, **kwargs):
        """This is unused, but required by the factory."""
        self.carrier_type = carrier_type
        self.action = action


def action(f):
    """
    Decorator for carrier actions. Use it to register an action in the
    factory and to validate input and output data.

    The decorated method must have an `input` argument decorated with a type hint
    and a return type hint.

    Example:
    ```python
    @action
    def get_label(self, input: CarrierLabelInput) -> CarrierLabelOutput:
        return CarrierLabelOutput.from_response(
            self.fetch(input.to_request())
        )
    ```
    """

    @wraps(f)
    def wrapper(self, carrier_type, action, data):
        hints = typing.get_type_hints(f)
        if "input" not in hints:
            raise ValueError(f"Missing input argument or type hint for {f}")
        if "return" not in hints:
            raise ValueError(f"Missing return type hint for {f}")

        try:
            input = hints["input"](**data)
        except Exception as e:
            raise InvalidApiInput(f"Invalid input data {data!r}\n\n{e!s}") from e

        try:
            rv = f(self, input)
        except CarrierError as e:
            raise e
        except Exception as e:
            raise CarrierError(None, f"Action failed {data!r}\n\n{e!s}") from e

        if isinstance(rv, hints["return"]):
            return rv.model_dump()

        return rv

    # Mark the function as an action for the metaclass
    wrapper.__action__ = True
    return wrapper
