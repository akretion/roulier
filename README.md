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
		"fristName": "Hparfr"
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

###Contributors


* [@hparfr](https://github.com/hparfr) ([Akretion.com](https://akretion.com))
* [@damdam-s](https://github.com/damdam-s) ([Camp2Camp.com](http://camptocamp.com))
* [@bealdav](https://github.com/bealdav) ([Akretion.com](https://akretion.com))