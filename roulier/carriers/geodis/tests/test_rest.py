# -*- coding: utf-8 -*-

import json
from collections import OrderedDict

from ..geodis_decoder_rest_ws import GeodisTrackingListApi, GeodisDecoderRestWs
from ..geodis_encoder_rest_ws import GeodisEncoderRestWs
from ..geodis_transport_rest_ws import GeodisTransportRestWs


def test_encode():
    encoder = GeodisEncoderRestWs()
    api = encoder.api('trackingList')
    payload = encoder.encode(api, 'trackingList')
    infos = payload['infos']
    assert infos['action'] == 'trackingList'
    assert infos['service'] in infos['url']


def test_transport_hash():
    """Ensure we encode the has the same way as the specification

    We create the exact same json as they (ordonned, separators)
    """
    api_key = "d89b703bfe0d440a966ff3d996f5936a"
    login = "QTTCLT"
    timestamp = "1546941256145"
    lang = "fr"
    service = "api/zoomclient/recherche-envois"
    params = OrderedDict([
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
    ])
    body = json.dumps(params, separators=(',', ':'))
    transport = GeodisTransportRestWs()
    hash = transport.get_hash(api_key, login, timestamp, lang, service, body)
    token = transport.get_token(login, timestamp, lang, hash)
    expected = (
        "QTTCLT;1546941256145;fr;" +
        "1b59ef28395469bdd3c823adc2603c469c657ed968e96375b0095307e0460fdf")
    assert token == expected


def test_decoder_visit():
    api = GeodisTrackingListApi()
    schema = {
        'str': 'simple_string',
        'int': 'simple_integer',
        'inner': {
            'inner_a': 'inner_a',
            'inner_b': 'inner_b',
        }
    }
    data = {
        'simple_string': 'abcdef',
        'simple_integer': 3,
        'inner_a': 'a',
        'inner_b': 'b',
    }
    ret = api.visit(data, schema)
    assert ret['str'] == data['simple_string']
    assert ret['int'] == data['simple_integer']
    assert ret['inner']['inner_a'] == data['inner_a']
