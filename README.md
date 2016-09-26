Roulier
===

Roulier is a shipping library written in Python.


Usage : 

```python
from roulier import roulier

laposte = roulier.get('laposte')

response = laposte.get({
	"infos": { 
		"contractNumber": "12345",
		"password": "password",
	},
	"service": {
		"productCode": "COL"
	},
	"parcel": {
		"insuranceValue": 0,
		"nonMachinable": False,
		"returnReceipt": False
	},
	"receiver_address": {
        "country": "DE",
        "zip": "93000"
   	}
}, "getProductInter")


print response

```


To get the full list of parameters:
```python

from roulier import roulier
laposte = roulier.get('laposte')
obj = laposte.api()

obj['infos']['contractNumber'] = '12345'
obj['infos']['password'] = 'password'
obj['service']['productCode'] = 'COL'
# ...

```

###Contributors


* [@hparfr](https://github.com/hparfr) ([Akretion.com](https://akretion.com))
* [@damdam-s](https://github.com/damdam-s) ([Camp2Camp.com](http://camptocamp.com))
