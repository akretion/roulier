# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import ClassVar

REMOVED = ClassVar[None]  # Hack to remove a field from inherited class


def prefix(data, prefix):
    return {f"{prefix}{k}": v for k, v in data.items()}


def suffix(data, suffix):
    return {f"{k}{suffix}": v for k, v in data.items()}


def clean_empty(data):
    return {k: v for k, v in data.items() if v is not None and v != ""}


def none_as_empty(data):
    return {k: v if v is not None else "" for k, v in data.items()}
