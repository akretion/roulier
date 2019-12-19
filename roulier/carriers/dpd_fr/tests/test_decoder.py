from ..dpd_decoder import DpdDecoder

def test_decoder():
    payload = {
        u'shipments': [{u'shpId': 1006455008, u'returnParcels': None, u'returnShpId': None, 
        u'masterParcelId': None, u'manifestId': 223556, u'parcels': [u'10770941402847']}],
        u'label': 
            {u'fileType': u'ZPL',
            u'fileContent': u'some_base_64',
            u'fileName': u'web_label2101335320191217_17090960.zpl'
            }
        }


    expected = {
        "tracking": {
            "number": "10770941402847"
        },
        "label": {
            "name": "web_label2101335320191217_17090960.zpl",
            "data": "some_base_64",
            "type": "ZPL"
        },
        "parcels": [
            {
                "id": "10770941402847",
                "number": "10770941402847",
                "reference": 'some ref',
                "label": {
                    "name": "web_label2101335320191217_17090960.zpl",
                    "data": "some_base_64",
                    "type": "ZPL"
                },
            }
        ],
        "annexes": [],
    }

    decoder = DpdDecoder()
    mapped = decoder.decode(payload, {"parcels": [{'cref1': 'some ref'}]}, 'createShipmentWithLabels')
    assert mapped==expected