# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..helpers import (
    filter_empty,
    merge,
    none_as_empty,
    prefix,
    suffix,
    unaccent,
    walk_data,
)


def test_prefix():
    assert prefix({"a": 1, "b": 2}, "p_") == {"p_a": 1, "p_b": 2}


def test_suffix():
    assert suffix({"a": 1, "b": 2}, "_s") == {"a_s": 1, "b_s": 2}


def test_walk_data():
    assert walk_data(
        {
            "a": 1,
            "b": {
                "c": 3,
                "d": {"a": 5, "f": 6},
            },
        }
    ) == {
        "a": 1,
        "b": {
            "c": 3,
            "d": {"a": 5, "f": 6},
        },
    }
    assert walk_data(
        {
            "a": 1,
            "b": {
                "c": 3,
                "d": {"a": 5, "f": 6},
            },
        },
        filter=lambda x: x not in [1, 5],
    ) == {"b": {"c": 3, "d": {"f": 6}}}
    assert walk_data(
        {
            "a": 1,
            "b": {
                "c": 3,
                "d": {"a": 5, "f": 6},
            },
        },
        transform=lambda x: x + 1,
    ) == {
        "a": 2,
        "b": {
            "c": 4,
            "d": {"a": 6, "f": 7},
        },
    }


def test_filter_empty():
    assert filter_empty(
        {
            "a": 1,
            "b": None,
            "c": "",
        }
    ) == {"a": 1}
    assert filter_empty(
        {
            "a": 1,
            "b": {"c": None, "d": {"a": 5, "f": ""}},
        }
    ) == {
        "a": 1,
        "b": {"d": {"a": 5}},
    }


def test_none_as_empty():
    assert none_as_empty({"a": 1, "b": None}) == {"a": 1, "b": ""}


def test_unaccent():
    assert unaccent("éà") == "ea"
    assert unaccent({"a": "éà", "b": {"c": 12, "d": ["çô", "ë"]}}) == {
        "a": "ea",
        "b": {"c": 12, "d": ["co", "e"]},
    }


def test_merge():
    assert merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}
    assert merge({"a": 1}, {"a": None}) == {"a": 1}
    assert merge({"a": 1}, {"a": ""}) == {"a": 1}
    assert merge({"a": None}, {"a": 1}) == {"a": 1}
    assert merge({"a": ""}, {"a": 1}) == {"a": 1}
    assert merge({"a": 1}, {"a": 2}, {"a": 3}) == {"a": 3}
    assert merge(
        {
            "a": {"b": 1},
        },
        {
            "a": {"c": 2},
        },
    ) == {
        "a": {"b": 1, "c": 2},
    }
    assert merge({"a": {"b": 1}}, {"a": {"b": 2}}) == {"a": {"b": 2}}
    assert merge({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": 3}}) == {"a": {"b": 3}}
    assert merge({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": None}}) == {
        "a": {"b": 2}
    }
    assert merge({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": ""}}) == {"a": {"b": 2}}
    assert merge({"a": {"b": 1}}, {"a": {"b": None}}, {"a": {"b": 3}}) == {
        "a": {"b": 3}
    }
    assert merge({"a": {"b": 1}}, {"a": {"b": ""}}, {"a": {"b": 3}}) == {"a": {"b": 3}}
    assert merge(
        {"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": 3}}, {"a": {"b": None}}
    ) == {"a": {"b": 3}}
    assert merge({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": 3}}, {"a": {"b": ""}})
