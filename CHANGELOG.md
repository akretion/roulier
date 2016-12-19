
# 0.1.1 

Roadmap / TODO: 
	- Add Kuehne & Nagel carrier
	- Add UPS carrier
	- Support test_mode for some carriers
	- Improve documentation
	- Support additionnal methods of api
	- Support carrier tracking
	- Write tests

# 0.1.0 2016-12-19

### BREAKING CHANGES
	- Laposte API has changed, lot of fields have been renamed
		Do `roulier.get('laposte').api()` to get the new fields.
		Reason for this change: be constitant with upcoming carriers.
		Response of get_label had changed

### Features / Refactorings
	- Use cerberus for data validation
	- Simplify api
	- Add carrier Geodis
	- Add carrier DPD France
	- Add get_carriers()
	- Improve documentation


# 0.0.1 - 2016-09-26

	- Publication on pypy https://pypi.python.org/pypi/roulier

# 0.0.0 - 2016

	- Add carrier Laposte
	- Add carrier Dummy (example)	
