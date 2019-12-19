from ..dpd_api import DpdApiGetLabelMappingIn

def test_clean_empty():
    # some unit tests
    _clean_empty = DpdApiGetLabelMappingIn()._clean_empty
    # empty dicts and empty list are not removed
    data = { "one": "", "two": 12, "three": [] }
    expected = { "two": 12 }
    assert _clean_empty(data) == expected

    data = {"a": { "b": 1, "c": "", "d": {"e": "", "f":2}}}
    expected= {"a": {"b": 1, "d": {"f": 2}}}
    assert _clean_empty(data) == expected

    data = {"a": { "b": 1, "c": "", "d": {"e": ""}}}
    expected= {"a": {"b": 1, "d": {}}}
    assert _clean_empty(data) == expected

    data =[1, "2", "", "4", {"5": ""}]
    expected =[1, "2", "4", {}]
    assert _clean_empty(data) == expected
