# -*- coding: utf-8 -*-
from datetime import date
import json
from collections import OrderedDict

from ..geodis_decoder_rest_ws import GeodisDecoderRestWs
from ..geodis_encoder_rest_ws import GeodisEncoderRestWs
from ..geodis_transport_rest_ws import GeodisTransportRestWs
from ..geodis_api_rest_ws import GeodisApiTrackingListOut


def test_encode():
    encoder = GeodisEncoderRestWs()
    api = encoder.api("trackingList")
    payload = encoder.encode(api, "trackingList")
    infos = payload["infos"]
    assert infos["action"] == "trackingList"
    assert infos["service"] in infos["url"]


def test_encode_api():
    encoder = GeodisEncoderRestWs()
    data = encoder.api("trackingList")

    data["service"]["shippingDateStart"] = date(2019, 7, 2)
    data["service"]["shippingDateEnd"] = date(2019, 7, 2)
    data["auth"]["login"] = "Akretion"
    data["auth"]["password"] = "121221789271"

    payload = encoder.encode(data, "trackingList")
    body = payload["body"]
    assert body["dateDepartFin"] == "2019-07-02"


def test_transport_hash():
    """Ensure we encode the has the same way as the specification

    We create the exact same json as they (ordonned, separators)
    """
    api_key = "d89b703bfe0d440a966ff3d996f5936a"
    login = "QTTCLT"
    timestamp = "1546941256145"
    lang = "fr"
    service = "api/zoomclient/recherche-envois"
    params = OrderedDict(
        [
            ("dateDepart", ""),
            ("dateDepartDebut", "2018-12-09"),
            ("dateDepartFin", "2019-01-08"),
            ("noRecepisse", ""),
            ("reference1", ""),
            ("cabColis", ""),
            ("noSuivi", ""),
            ("codeSa", "084135"),
            ("codeClient", ""),
            ("codeProduit", ""),
            ("typePrestation", "EXP"),
            ("dateLivraison", ""),
            ("refDest", ""),
            ("nomDest", ""),
            ("codePostalDest", ""),
            ("natureMarchandise", ""),
        ]
    )
    body = json.dumps(params, separators=(",", ":"))
    transport = GeodisTransportRestWs()
    hash = transport.get_hash(api_key, login, timestamp, lang, service, body)
    token = transport.get_token(login, timestamp, lang, hash)
    expected = (
        "QTTCLT;1546941256145;fr;"
        + "1b59ef28395469bdd3c823adc2603c469c657ed968e96375b0095307e0460fdf"
    )
    assert token == expected


def test_decoder_visit():
    api = GeodisApiTrackingListOut()
    schema = {
        "str": "simple_string",
        "int": "simple_integer",
        "inner": {"inner_a": "inner_a", "inner_b": "inner_b",},
    }
    data = {
        "simple_string": "abcdef",
        "simple_integer": 3,
        "inner_a": "a",
        "inner_b": "b",
        "no_lookup": "should not fail",
    }
    ret = api.visit(data, schema)
    assert ret["str"] == data["simple_string"]
    assert ret["int"] == data["simple_integer"]
    assert ret["inner"]["inner_a"] == data["inner_a"]


data = (
    """{"contenu": [{"statutServicesLivraison": "","""
    """ "libelleLongEtat": "Livr\u00e9e", "dateEtat": "2019-07-10","""
    """ "libelleLivraison": "Livraison le", "emissionEqc": null,"""
    """ "libelleStatutServicesLivraison": "", "adresse1Exp": "axxxZ","""
    """ "villeExp": "STRASBOURG", "temperatureMin": null, "codeOption":"""
    """ "RET", "libellePrestation": "Retour/Trans. Fr. - Express","""
    """ "urlPreuveService": "", "adresse2Exp": "wcvwv", "dateEtatFrs":"""
    """ "10/07/2019", "avecMatiereDangereuse": false, "dateDepartFrs":"""
    """ "09/07/2019", "urlImageEnlevementLivraison":"""
    """ "http://github.com/akretion/roulier", "emissionEqa": null,"""
    """ "dateLivraisonFrs": "10/07/2019", "noRecepisse": "12212122","""
    """ "nbErreursNotification": 0, "listServicesLivraison": [],"""
    """ "delaiInstruction": 0, "adresse1Dest": "27 rue Henri Rolland","""
    """ "libellePaysExp": "France","""
    """ "codePostalExp": "69100", "envoiRegroupement": false,"""
    """ "refDest": "", "temperatureMed": null,"""
    """ "dateLimiteInstruction": null, "nomDest": "TdsdsfsfsfsT","""
    """ "avecInstructionDonnee": false, "uniteInstruction": "", "refUniEnl":"""
    """ 1212121221, "libelleEtat": "Livr\u00e9e", "nomExp": "RETOUR","""
    """ "urlSuiviDestinataire": "https://akretion.com", "adresse2Dest": "","""
    """ "emissionPar": null, "codePaysDest": "FR", "nbExcursionsTemp": null,"""
    """ "noRecepRegroupement": "", "envoiRegroupe": false, "reference1":"""
    """ "abcdeefefefe", "dateLivraison": "2019-07-10", "loginDestinataire":"""
    """ "12121212121", "nbPalettes": 0, "refUniExp": 1212212121,"""
    """ "avecAttenteInstruction": false, "codePaysExp": "FR", "codeClient":"""
    """ "01234", "listEnvoisRegroupes": [], "codeProduit": "ENE","""
    """ "codeJustification": "NEM", "villeDest": "LESQUIN", "nbColis": 2,"""
    """ "codePostalDest": "59810", "libellePaysDest": "France","""
    """ "typePrestation": "EXP", "refUniRegroupement": 0, "codeSa":"""
    """ "122121", "noSuivi": "12122121", "dateLimiteInstructionFrs": "","""
    """ "codeSituation": "LIV", "dateDepart": "2019-07-09","""
    """ "temperatureMax": null, "poids": 9.0, "reference2": ""},"""
    """ {"statutServicesLivraison": "", "libelleLongEtat": "Livr\u00e9e","""
    """ "dateEtat": "2019-07-10", "libelleLivraison": "Livraison le","""
    """ "emissionEqc": null, "libelleStatutServicesLivraison": "","""
    """ "adresse1Exp": "Akretion", "villeExp": "VILLEURBANNE","""
    """ "temperatureMin": null, "codeOption": "RET","""
    """ "libellePrestation": "Retour/Trans. Fr. - Express","""
    """ "urlPreuveService": "", "adresse2Exp":"""
    """ "GRAND", "dateEtatFrs": "10/07/2019", "avecMatiereDangereuse":"""
    """ false, "dateDepartFrs": "09/07/2019","""
    """ "urlImageEnlevementLivraison": "http://github.com/akretion/roulier","""
    """ "emissionEqa": null, "dateLivraisonFrs": "10/07/2019", """
    """ "noRecepisse": "1212121ae", "nbErreursNotification": 0,"""
    """ "listServicesLivraison": [], "delaiInstruction": 0,"""
    """ "adresse1Dest": "27 Rue Henri Rolland","""
    """ "libellePaysExp": "France", "codePostalExp": "69100","""
    """ "envoiRegroupement": false, "refDest": "","""
    """ "temperatureMed": null, "dateLimiteInstruction": null, "nomDest":"""
    """ "Akretion", "avecInstructionDonnee": false, "uniteInstruction":"""
    """ "", "refUniEnl": 121212, "libelleEtat": "Livr\u00e9e", "nomExp":"""
    """ "RETOUR POUR AVARIE", "urlSuiviDestinataire": "http://akretion.com","""
    """ "adresse2Dest": "", "emissionPar": null, "codePaysDest": "FR","""
    """ "nbExcursionsTemp": null, "noRecepRegroupement": "","""
    """ "envoiRegroupe": false, "reference1": "Shopinvader","""
    """ "dateLivraison": "2019-07-10", "loginDestinataire": "1279217912121","""
    """ "nbPalettes": 0, "refUniExp": 12321212,"""
    """ "avecAttenteInstruction": false, "codePaysExp": "FR", "codeClient":"""
    """ "1212121", "listEnvoisRegroupes": [], "codeProduit": "ENE","""
    """ "codeJustification": "NEM", "villeDest": "Villeurbanne","""
    """ "nbColis": 2, "codePostalDest": "69100","""
    """ "libellePaysDest": "France","""
    """ "typePrestation": "EXP", "refUniRegroupement": 0, "codeSa": "12121","""
    """ "noSuivi": "12212121", "dateLimiteInstructionFrs": "","""
    """ "codeSituation": "LIV", "dateDepart": "2019-07-09","""
    """ "temperatureMax": null, "poids":"""
    """ 5.0, "reference2": ""}], "codeErreur": null,"""
    """ "ok": true, "texteErreur": null}"""
)

ret_val = [
    {
        "from_address": {
            "city": u"STRASBOURG",
            "country": u"FR",
            "country_name": u"France",
            "name": u"RETOUR",
            "street1": u"axxxZ",
            "street2": u"wcvwv",
            "zip": u"69100",
        },
        "parcels": {"weight": 9.0},
        "service": {
            "agencyId": u"122121",
            "customerId": u"01234",
            "option": u"RET",
            "product": u"ENE",
            "reference1": u"abcdeefefefe",
            "reference2": u"",
            "reference3": u"",
            "shippingDate": u"2019-07-09",
            "shippingId": u"12212122",
        },
        "to_address": {
            "city": u"LESQUIN",
            "country": u"FR",
            "country_name": u"France",
            "name": u"TdsdsfsfsfsT",
            "street1": u"27 rue Henri Rolland",
            "street2": u"",
            "zip": u"59810",
        },
        "tracking": {
            "estDeliveryDate": u"2019-07-10",
            "proofUrl": u"http://github.com/akretion/roulier",
            "publicUrl": u"https://akretion.com",
            "status": "DELIVERED",
            "statusDate": u"2019-07-10",
            "statusDetails": u"Livr\xe9e",
            "trackingCode": u"12122121",
        },
    },
    {
        "from_address": {
            "city": u"VILLEURBANNE",
            "country": u"FR",
            "country_name": u"France",
            "name": u"RETOUR POUR AVARIE",
            "street1": u"Akretion",
            "street2": u"GRAND",
            "zip": u"69100",
        },
        "parcels": {"weight": 5.0},
        "service": {
            "agencyId": u"12121",
            "customerId": u"1212121",
            "option": u"RET",
            "product": u"ENE",
            "reference1": u"Shopinvader",
            "reference2": u"",
            "reference3": u"",
            "shippingDate": u"2019-07-09",
            "shippingId": u"1212121ae",
        },
        "to_address": {
            "city": u"Villeurbanne",
            "country": u"FR",
            "country_name": u"France",
            "name": u"Akretion",
            "street1": u"27 Rue Henri Rolland",
            "street2": u"",
            "zip": u"69100",
        },
        "tracking": {
            "estDeliveryDate": u"2019-07-10",
            "proofUrl": u"http://github.com/akretion/roulier",
            "publicUrl": u"http://akretion.com",
            "status": "DELIVERED",
            "statusDate": u"2019-07-10",
            "statusDetails": u"Livr\xe9e",
            "trackingCode": u"12212121",
        },
    },
]


def test_decode():
    payload = json.loads(data)
    rep = {
        "body": payload.get("contenu", []),
        "parts": [],
        "response": None,
    }
    decode = GeodisDecoderRestWs()
    ret = decode.decode(rep, "trackingList")

    assert ret == ret_val
