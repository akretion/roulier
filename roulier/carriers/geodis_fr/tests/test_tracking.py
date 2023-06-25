from datetime import date
import json
from collections import OrderedDict

from ..tracking.decoder import GeodisFrTrackingListDecoder
from ..tracking.encoder import GeodisEncoderRestWs
from ..geodis_transport_rest import GeodisTransportRestWs
from ..tracking.api import GeodisApiTrackingListOut, GeodisApiTrackingList
from ..tracking.carrier_action import GeodisFrTrackingList

action = GeodisFrTrackingList("geodis_fr", "get_tracking_list")


def test_encode_api():
    encoder = GeodisEncoderRestWs(action)
    api = GeodisApiTrackingList(action)
    data = api.api_values()

    data["service"]["shippingDateStart"] = date(2019, 7, 2)
    data["service"]["shippingDateEnd"] = date(2019, 7, 2)
    data["auth"]["login"] = "Akretion"
    data["auth"]["password"] = "121221789271"

    payload = encoder.encode(data)
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
    transport = GeodisTransportRestWs(action)
    hash = transport.get_hash(api_key, login, timestamp, lang, service, body)
    token = transport.get_token(login, timestamp, lang, hash)
    expected = (
        "QTTCLT;1546941256145;fr;"
        + "1b59ef28395469bdd3c823adc2603c469c657ed968e96375b0095307e0460fdf"
    )
    assert token == expected


def test_decoder_visit():
    api = GeodisApiTrackingListOut(action)
    schema = {
        "str": "simple_string",
        "int": "simple_integer",
        "inner": {
            "inner_a": "inner_a",
            "inner_b": "inner_b",
        },
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
            "city": "STRASBOURG",
            "country": "FR",
            "country_name": "France",
            "name": "RETOUR",
            "street1": "axxxZ",
            "street2": "wcvwv",
            "zip": "69100",
        },
        "parcels": {"weight": 9.0},
        "service": {
            "agencyId": "122121",
            "customerId": "01234",
            "option": "RET",
            "product": "ENE",
            "reference1": "abcdeefefefe",
            "reference2": "",
            "reference3": "",
            "shippingDate": "2019-07-09",
            "shippingId": "12212122",
        },
        "to_address": {
            "city": "LESQUIN",
            "country": "FR",
            "country_name": "France",
            "name": "TdsdsfsfsfsT",
            "street1": "27 rue Henri Rolland",
            "street2": "",
            "zip": "59810",
        },
        "tracking": {
            "estDeliveryDate": "2019-07-10",
            "proofUrl": "http://github.com/akretion/roulier",
            "publicUrl": "https://akretion.com",
            "status": "DELIVERED",
            "statusDate": "2019-07-10",
            "statusDetails": "Livr\xe9e",
            "trackingCode": "12122121",
        },
    },
    {
        "from_address": {
            "city": "VILLEURBANNE",
            "country": "FR",
            "country_name": "France",
            "name": "RETOUR POUR AVARIE",
            "street1": "Akretion",
            "street2": "GRAND",
            "zip": "69100",
        },
        "parcels": {"weight": 5.0},
        "service": {
            "agencyId": "12121",
            "customerId": "1212121",
            "option": "RET",
            "product": "ENE",
            "reference1": "Shopinvader",
            "reference2": "",
            "reference3": "",
            "shippingDate": "2019-07-09",
            "shippingId": "1212121ae",
        },
        "to_address": {
            "city": "Villeurbanne",
            "country": "FR",
            "country_name": "France",
            "name": "Akretion",
            "street1": "27 Rue Henri Rolland",
            "street2": "",
            "zip": "69100",
        },
        "tracking": {
            "estDeliveryDate": "2019-07-10",
            "proofUrl": "http://github.com/akretion/roulier",
            "publicUrl": "http://akretion.com",
            "status": "DELIVERED",
            "statusDate": "2019-07-10",
            "statusDetails": "Livr\xe9e",
            "trackingCode": "12212121",
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
    decode = GeodisFrTrackingListDecoder(action)
    decode.decode(rep, False)
    ret = decode.result

    assert ret == ret_val
