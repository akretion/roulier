

Roadmap / TODO: 
	- Add Kuehne & Nagel carrier
	- Add Geodis EDI
	- Add UPS carrier
	- Support test_mode for some carriers
	- Improve documentation
	- Support additionnal methods of api
	- Write tests

# 0.1.4 2017-03-20
	- Automatic deployment to pypi

# 0.1.1 2017-03-20


### Features / Refactorings
	- Refactoring of error handling: exception are now always raised, returns code (success | warning) removed
	- Simplification of return code
	- Remove duplicate code of get_parts
	- Handling of additionnal attachments ("annexes")
	- tracking code is always in tracking.number
	- label is always in label.data

###	BREAKING CHANGES
	- errors are all raised with exceptions
	- raise Exception removed in favor of better defined exceptions
	- return of get_label harmonized


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
