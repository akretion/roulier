# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
import pytest

try:
    from .credentials import CREDENTIALS
except ImportError:
    from .credentials_demo import CREDENTIALS


@pytest.fixture(scope="session")
def credentials():
    return {
        **CREDENTIALS,
        "isTest": True,
    }


@pytest.fixture
def base_get_label_data():
    return {
        "service": {
            "shippingDate": date(2024, 1, 1),
            "labelFormat": "PDF",
        },
        "parcels": [{"weight": 1.2, "comment": "Fake comment"}],
        "from_address": {
            "name": "Akrétion",
            "street1": "27 rue Henri Rolland",
            "street2": "Batiment B",
            "city": "Villeurbanne",
            "zip": "69100",
            "country": "FR",
            "phone": "+33482538457",
        },
        "to_address": {
            "name": "Hügǒ",
            "firstName": "Victor",
            "street1": "6 Place des Vôsges",
            "city": "Paris",
            "zip": "75004",
            "country": "FR",
            "email": "hugo.victor@example.com",
            "phone": "+33600000000",
        },
    }


@pytest.fixture
def base_find_pickup_site_data():
    return {
        "search": {
            "country": "FR",
            "zip": "69100",
        },
    }
