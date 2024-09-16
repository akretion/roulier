# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import ClassVar
import unicodedata

REMOVED = ClassVar[None]  # Hack to remove a field from inherited class


def prefix(data, prefix):
    return {f"{prefix}{k}": v for k, v in data.items()}


def suffix(data, suffix):
    return {f"{k}{suffix}": v for k, v in data.items()}


def walk_data(data, filter=lambda x: True, transform=lambda x: x):
    if isinstance(data, dict):
        return {
            k: walk_data(v, filter, transform) for k, v in data.items() if filter(v)
        }
    elif isinstance(data, list):
        return [walk_data(v, filter, transform) for v in data]
    else:
        return transform(data)


def filter_empty(data):
    return walk_data(data, filter=lambda x: x is not None and x != "")


def none_as_empty(data):
    return walk_data(data, transform=lambda x: "" if x is None else x)


def unaccent(s):
    if isinstance(s, dict):
        return walk_data(s, transform=unaccent)
    if not isinstance(s, str):
        return s
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def merge(*dicts):
    # Recursively merge dictionaries
    result = {}
    for d in dicts:
        for k, v in d.items():
            if isinstance(v, dict):
                result[k] = merge(result.get(k, {}), v)
            else:
                if not v and result.get(k):
                    # Do not override value with empty value
                    continue
                result[k] = v
    return result
