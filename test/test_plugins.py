import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'filter_plugins'))
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'test_plugins'))

print(sys.path)

from custom_filters import reverse_record, filename, with_ext, \
    alias_keys, merge_dicts, merge_dicts_reverse, select_attributes, \
    drop_attributes, map_format, merge_item, key_item, dict_to_list, \
    list_to_dict, is_hash, to_dict  # noqa: E402
from custom_tests import test_network, test_property  # noqa: E402


def test_is_hash():
    assert is_hash({}) is True
    assert is_hash(dict()) is True
    assert is_hash("") is False
    assert is_hash([]) is False


def test_reverse_record():
    host = 'test.com'
    address = '10.0.0.1'
    r = {
        'host': host,
        'ip-address': address
    }
    rr = reverse_record(r)
    assert rr['ip-address'] == host
    assert rr['host'] == '1.0.0.10.in-addr.arpa'
    assert rr['type'] == 'PTR'


def test_filename():
    assert filename('basename.ext') == 'basename'
    assert filename('basename.ext1.ext2') == 'basename'
    assert filename('basename') == 'basename'


def test_with_ext():
    assert with_ext('basename.ext', 'newext') == 'basename.newext'
    assert with_ext('basename.ext1.ext2', 'newext') == 'basename.newext'
    assert with_ext('basename', 'newext') == 'basename.newext'


def test_test_network():
    host = 'test.com'
    address = '10.0.0.1'
    r = {
        'host': host,
        'address': address
    }
    assert not test_network(r)
    assert not test_network(r, '10.0.0.0/24')
    assert not test_network(r, '10.1.0.0/24')
    assert test_network(r, '10.0.0.0/24', 'address') == r


def test_test_property():
    host = 'test.com'
    address = '10.0.0.1'
    r = {
        'host': host,
        'address': address
    }
    assert not test_property(r, '.*', 'none')
    assert not test_property(r, 'nomatch', 'host')
    assert test_property(r, '.*.com', 'host') == r


def test_alias_keys():
    assert alias_keys({}, {}) == {}
    assert alias_keys({'a': 1}, {'a': 'b'}) == {'a': 1, 'b': 1}
    assert alias_keys({'a': 1, 'b': 2},
                      {'a': 'c', 'b': 'd'}) == {'a': 1, 'b': 2, 'c': 1, 'd': 2}
    assert alias_keys({'a': 1},
                      {'a': 'b', 'b': 'c'}) == {'a': 1, 'b': 1, 'c': 1}


def test_merge_dicts():
    assert merge_dicts({}, {}) == {}
    assert merge_dicts({'a': '0'}, {'a': '1'}) == {'a': '1'}
    assert merge_dicts({'a': '0', 'b': '1'},
                       {'a': '2', 'b': '3'}) == {'a': '2', 'b': '3'}
    assert merge_dicts({'a': '0'},
                       {'a': '1', 'b': '2'}) == {'a': '1', 'b': '2'}
    assert merge_dicts({'a': '0', 'b': '1'},
                       {'a': '2'}) == {'a': '2', 'b': '1'}


def test_merge_dicts_reverse():
    assert merge_dicts_reverse({}, {}) == {}
    assert merge_dicts_reverse({'a': '0'}, {'a': '1'}) == {'a': '0'}
    assert merge_dicts_reverse({'a': '0', 'b': '1'},
                               {'a': '2', 'b': '3'}) == {'a': '0', 'b': '1'}
    assert merge_dicts_reverse({'a': '0'},
                               {'a': '1', 'b': '2'}) == {'a': '0', 'b': '2'}
    assert merge_dicts_reverse({'a': '0', 'b': '1'},
                               {'a': '2'}) == {'a': '0', 'b': '1'}


def test_select_attributes():
    assert select_attributes({'a': '0', 'b': '1'}, ['a']) == {'a': '0'}
    assert select_attributes({'a': '0', 'b': '1'}, []) == {}
    assert select_attributes({'a': '0', 'b': '1'},
                             ['a', 'b']) == {'a': '0', 'b': '1'}
    assert select_attributes({'a': '0'}, ['a', 'b']) == {'a': '0'}


def test_drop_attributes():
    assert drop_attributes({'a': '0', 'b': '1'}, ['a']) == {'b': '1'}
    assert drop_attributes({'a': '0', 'b': '1'}, []) == {'a': '0', 'b': '1'}
    assert drop_attributes({'a': '0', 'b': '1'}, ['a', 'b']) == {}
    assert drop_attributes({'a': '0'}, ['c']) == {'a': '0'}


def test_to_dict():
    assert to_dict([['a', 'b']]) == {'a': 'b'}
    assert to_dict({'a': 'b'}, 'c') == {'c': {'a': 'b'}}
    assert to_dict(['a', 'b'], 'c') == {'c': ['a', 'b']}
    assert to_dict('a', {'a': 'first', 'b': 'second'}) == {'a': 'first',
                                                           'b': 'second'}
    assert to_dict('a', {'a': 'first', 'b': '%s'}) == {'a': 'first',
                                                       'b': 'a'}


def test_map_format():
    assert map_format('', '%sx') == 'x'
    assert map_format('a', '%sx') == 'ax'
    assert map_format('a', 'x%s') == 'xa'
    assert map_format('a', '%s') == 'a'
    assert map_format('a', '') == ''
    assert map_format({'a': 'first'}, {'b': 'x%s'}) == {'a': 'first'}
    assert map_format({'a': 'first'}, {'a': 'x%s'}) == {'a': 'xfirst'}
    assert map_format({'a': 'first'}, {'a': '%sx'}) == {'a': 'firstx'}
    assert map_format({'a': 'first'}, {'a': 'second'}) == {'a': 'second'}


def test_merge_item():
    d = {
        'a': 'first'
    }
    assert merge_item(['second', d], 'b') == {'a': 'first', 'b': 'second'}
    assert merge_item(['second', {}], 'b') == {'b': 'second'}
    assert merge_item(['second', d], 'a') == {'a': 'second'}


def test_key_item():
    d = {
        'a': 'first',
        'b': 'second'
    }
    assert key_item(d, 'a') == ['first', {'b': 'second'}]
    assert key_item(d, 'b') == ['second', {'a': 'first'}]


def test_dict_to_list():
    d = {
        'a': {
            'content': 'first'
        },
        'b': {
            'content': 'second'
        }
    }
    assert dict_to_list(d, 'key') == [{'key': 'a', 'content': 'first'},
                                      {'key': 'b', 'content': 'second'}]


def test_list_to_dict():
    d = {
        'a': {
            'content': 'first'
        },
        'b': {
            'content': 'second'
        }
    }
    lx = dict_to_list(d, 'key')
    assert list_to_dict(lx, 'key') == d
    assert list_to_dict(lx, 'key', False) == {
        'a': {
            'content': 'first',
            'key': 'a'
        },
        'b': {
            'content': 'second',
            'key': 'b'
        }
    }
