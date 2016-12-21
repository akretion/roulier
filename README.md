Roulier
===

Roulier is a shipping library written in Python for sending parcels.
Roulier will get a label + tracking number to your carrier for you.


![big picture](overview.svg)


* Roulier runs on your server and call each carrier API directly.
* You have to use your own credentials provided by each carriers.
* Roulier is Open Source software, AGPL-3
* Roulier integrate a multitude of carriers : Laposte, Geodis, DPD, K&N... more to come.



### Usage

```python
from roulier import roulier

laposte = roulier.get('laposte')

response = laposte.get_label({
	"auth": { 
		"login": "12345",
		"password": "password",
	},
	"service": {
		"productCode": "COL"
	},
	"parcel": {
		"weight": 3.4,
	},
	"to_address": {
		"firstName": "Hparfr"
		"street1": "35 b Rue Montgolfier"
		"city": "Villeurbanne"
        "country": "FR",
        "zip": "69100"
   	},
   	"from_address": {
		"fristName": "Akretion France"
		"street1": "35 b Rue Montgolfier"
		"city": "Villeurbanne"
        "country": "FR",
        "zip": "69100"
   	},
})


print response

```


Get supported carriers:
```python
from roulier import roulier
print roulier.get_carriers()
```

To get the full list of parameters:
```python
from pprint import pprint
from roulier import roulier


laposte = roulier.get('laposte')
pprint(laposte.api())

# ...

```

Advanced usage for Laposte

Usefull for debugging: get the xml before the call, send an xml directly, analyse the response

```python
from roulier import roulier
laposte = roulier.get('laposte')

#0) create dict for the request as usually 
api = laposte.api();
api['auth']['login'] = '12345'
...

# 1) get the sls xml: 
req = laposte.encoder.encode(api, 'generateLabelRequest')
# req['body'] contains the xml payload (<sls:generateLabel xmlns:sls="http://sls.ws.coliposte.fr">...</sls:generateLabel>)

# 2) get the soap message
soap_request = laposte.ws.soap_wrap(req['body'], req['headers'])
#soap_request is a string (xml)

# 3) send xml_request to ws
soap_response = laposte.ws.send_request(xml_request)
# soap_response is a Requests response

# 4) interpret the response
data = laposte.ws.handle_response(soap_response)

# 5)get the raw Request Response:
data['response'] 


```
It's more or less the same for every carrier with SOAP webservice.


Validate input

For input validate we use [Cerberus](http://docs.python-cerberus.org/en/stable/)
```python
from roulier import roulier
laposte = roulier.get('laposte')

# get a ready to fill dict with default values:
laposte.api()


# advanced usage : 
from roulier.carriers.laposte.laposte_api import LaposteApi
l_api = LaposteApi()

# get the full schema:
l_api.api_schema()

# validate a dict against the schema
a_dict = { 'auth': {'login': '', 'password': 'password'}, ... }
l_api.errors(a_dict)
# > {'auth': [{'login': ['empty values not allowed']}], ...}

# get a part of schema (like 'parcel')
l_api._parcel()
```


###Contributors


* [@hparfr](https://github.com/hparfr) ([Akretion.com](https://akretion.com))
* [@damdam-s](https://github.com/damdam-s) ([Camp2Camp.com](http://camptocamp.com))
* [@bealdav](https://github.com/bealdav) ([Akretion.com](https://akretion.com))


### Dependencies

* [Cerberus](http://docs.python-cerberus.org/) - input validation and normalization
* [lxml](http://lxml.de/) - XML parsing
* [Jinja2](http://jinja.pocoo.org/) - templating
* [Requests](http://docs.python-requests.org/) - HTTP requests
* [zplgrf](https://github.com/kylemacfarlane/zplgrf) - PNG to ZPL conversion
