# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from roulier import roulier
from roulier.carrier import Carrier, action
from roulier.exception import CarrierError, InvalidApiInput
from pydantic import BaseModel
import pytest


@pytest.fixture(autouse=True)
def reset_roulier():
    roulier.factory._carrier_action = {}


def test_carrier_api():
    assert "dummy" not in roulier.get_carriers_action_available()

    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(outname=data.name, outid=data.id)

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            assert input.name == "test"
            assert input.id == 1

            return DummyOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get"]

    rv = roulier.get("dummy", "get", {"name": "test", "id": 1})
    assert rv == {"outname": "test", "outid": 1}


def test_carrier_api_unexposed():
    class DummySubIn(BaseModel):
        key: str

    class DummyIn(BaseModel):
        name: str | None = None
        subs: list[DummySubIn]

    class DummyOut(BaseModel):
        len: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(len=len(data.subs))

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        def unexposed(self, input: DummyIn) -> DummyOut:
            """This should not be exposed."""

        @action
        def acquire(self, input: DummyIn) -> DummyOut:
            assert input.name == None
            assert len(input.subs) == 2
            return DummyOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["acquire"]

    rv = roulier.get("dummy", "acquire", {"subs": [{"key": "test"}, {"key": "test2"}]})
    assert rv == {"len": 2}


def test_carrier_api_bad_input_signature():

    class DummyOut(BaseModel):
        pass

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input) -> DummyOut:
            pass

    with pytest.raises(ValueError) as excinfo:
        roulier.get("dummy", "get", {})
    assert "Missing input argument or type hint" in str(excinfo.value)


def test_carrier_api_bad_output_signature():
    class DummyIn(BaseModel):
        pass

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn):
            pass

    with pytest.raises(ValueError) as excinfo:
        roulier.get("dummy", "get", {})
    assert "Missing return type hint" in str(excinfo.value)


def test_carrier_api_invalid_input():
    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(outname=data.name, outid=data.id)

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            return DummyOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get"]

    with pytest.raises(InvalidApiInput) as excinfo:
        roulier.get("dummy", "get", {"description": "test", "id": 1})

    assert "Invalid input data" in str(excinfo.value)
    assert "name\n  Field required" in str(excinfo.value)


def test_carrier_api_invalid_output():
    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(out=data.name)

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            return DummyOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get"]

    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dummy", "get", {"name": "test", "id": 1})

    assert "Action failed" in str(excinfo.value)
    assert "outname\n  Field required" in str(excinfo.value)


def test_carrier_api_carrier_error():
    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(outname=data.name, outid=data.id)

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            raise CarrierError({"url": "http://fail"}, "This failed miserably")

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get"]

    with pytest.raises(CarrierError) as excinfo:
        roulier.get("dummy", "get", {"name": "test", "id": 1})

    assert "This failed miserably" in str(excinfo.value)
    assert excinfo.value.response == {"url": "http://fail"}


def test_carrier_api_extra_input():
    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(outname=data.name, outid=data.id)

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            return DummyOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get"]

    rv = roulier.get("dummy", "get", {"name": "test", "description": "test", "id": 1})
    assert rv == {"outname": "test", "outid": 1}


def test_carrier_api_multi_actions():
    class DummyIn(BaseModel):
        name: str
        id: int

    class DummyOut(BaseModel):
        outname: str
        outid: int

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(outname=data.name, outid=data.id)

    class DummyAcquireOut(BaseModel):
        out: str

        @classmethod
        def from_in(cls, data: DummyIn):
            return cls(out=f"[{data.id}] {data.name}")

    class DummyCarrier(Carrier):
        __key__ = "dummy"

        @action
        def get(self, input: DummyIn) -> DummyOut:
            return DummyOut.from_in(input)

        @action
        def acquire(self, input: DummyIn) -> DummyAcquireOut:
            return DummyAcquireOut.from_in(input)

    assert "dummy" in roulier.get_carriers_action_available()
    assert roulier.get_carriers_action_available()["dummy"] == ["get", "acquire"]

    rv = roulier.get("dummy", "get", {"name": "test", "description": "test", "id": 1})
    assert rv == {"outname": "test", "outid": 1}

    rv = roulier.get(
        "dummy", "acquire", {"name": "test", "description": "test", "id": 1}
    )
    assert rv == {"out": "[1] test"}
