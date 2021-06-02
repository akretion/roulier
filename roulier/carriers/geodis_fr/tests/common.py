from vcr_unittest import VCRTestCase


# If you need to re-generate cassettes and really call webservice, you have to create
# a file secret.py in the "tests" folder and configure a dict like this :
# secrets = {
#     "login": "Real login",
#     "password": "real password",
# }
# these data will then be replaced by dummy data in the cassette.yaml file

try:
    from .secret import secrets

    login = secrets["login"]
    password = secrets["password"]
    customer_id = secrets["customer_id"]
except ImportError:
    login = "account_test_number"
    password = "123456789101"
    customer_id = "158741"


def hide_sensitive_data(request):
    body = request.body
    body = body.replace(login.encode(), "account_test_number".encode())
    body = body.replace(password.encode(), "123456789101".encode())
    body = body.replace(customer_id.encode(), "158741".encode())
    request.body = body
    return request


def insert_real_secrets(payload):
    if payload.get("auth", {}).get("login"):
        payload["auth"]["login"] = login
    if payload.get("auth", {}).get("password"):
        payload["auth"]["password"] = password
    if payload.get("service", {}).get("customerId"):
        payload["service"]["customerId"] = customer_id


class GeodisVcrCommon(VCRTestCase):
    def setUp(self):
        super().setUp()

    def _get_vcr_kwargs(self, **kwargs):
        return {
            "before_record_request": hide_sensitive_data,
        }
