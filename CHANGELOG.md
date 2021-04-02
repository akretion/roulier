
Roadmap / TODO: 

	- Add Kuehne & Nagel carrier
	- Add UPS carrier
	- Add geodis carrier
	- Add dpd rest api
	- Improve documentation
	- Support additionnal methods of api
	- Write more tests
	- generate api documentation

# 1.1.0 2021-04-02
    - Add GLS rest api
    - Fix GLS glsbox api and manage expedition outside France
    - Add DPD soap api for python 3
    - Improve/complete Laposte Soap api for CN23
    - Unify/refactore the way to manage shippingDate (same input format for all carriers)

# 1.0.0 2020-12-08
    - Refactore library design to be able to re-use some logic between carriers
    - Add compatibility with python 3
    - Remove compatibility with python 2 (check versions < 1.0.0 for that)
    - Adapt laposte and chronopost to python 3
    - Add gls France support
    - standardize output for all supported carriers

# 0.3.9 2019-09-12
    - Improve setup.py

# 0.3.8 2019-09-12
    - Geodis: add Zoom API implementation (tracking)
    - Geodis: name specifications in comments in geodis.py
    - Geodis: add tests about Zoom Api
    - Geodis: GeodisDecoder -> GeodisDecoderWs
    - Add tests in .travis

# 0.3.7 2019-01-07
    - Geodis: fix sending company name
    - Geodis: fix coerce for EDI
    - Add coercing for oe

# 0.3.5 2018-11-26
        - Add requirements.txt

# 0.3.4 2018-11-26
        - DPD convert characters to ASCII (because issues on labels) 

# 0.3.3 2018-02-19
	- Geodis force ASCII conversion for EDI.

# 0.3.2 2018-02-06
	- Geodis fix missing CTA segment

# 0.3.1 2018-02-01
	- Geodis fix typo in (e)mail

# 0.3.0 2018-02-01

### Features / Refactorings
	- Geodis add options like (rdv)
	- Geodis add notifications (by mail or sms)
	- Geodis add new method : findLocalite (check address based on city or zip)
	- Geodis refactoring internals of WS

###	BREAKING CHANGES
	- Geodis WS api: option is now named priority

# 0.2.1 2017-12-19
	- fix Geodis EDI escaping, remplace by special chars by spaces

# 0.2.0 2017-11-03

### Features / Refactorings
	- add Geodis EDI
	- allow multiparcel (only for GEODIS)
	(Not possible for Laposte API and not implemented for DPD)

###	BREAKING CHANGES
	- parcels should be used instead of parcel. Easy fix: suffix parcel with an "s" and wrap value with []
	- new parcels key added in response


# 0.1.6 2017-07-27
	- DPD concat street2 to street1 (no street2 in DPD API)
	- DPD concat company to name (no name in DPD API)


# 0.1.5 2017-05-02
	- fix escaping issue in DPD
	- fix output of DPD (now always base64 decoded)

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
