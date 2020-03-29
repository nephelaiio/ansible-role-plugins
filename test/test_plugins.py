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
    list_to_dict, is_hash, to_dict, to_kv, to_safe_yaml, map_values, \
    map_attributes  # noqa: E402
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


def test_map_attributes():
    assert map_attributes({'a': '0', 'b': '1'}, ['a']) == ['0']
    assert map_attributes({'a': '0', 'b': '1'}, []) == []
    assert map_attributes({'a': '0', 'b': '1'}, ['c']) == []
    assert map_attributes({'a': '0', 'b': '1'},
                          ['a', 'b']) == ['0', '1']
    assert map_attributes({'a': '0', 'b': '1'},
                          ['b', 'a']) == ['1', '0']
    assert map_attributes({'a': '0'}, ['a', 'b']) == ['0']


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
    assert to_dict('a', {'%s_1': 'first', '%s_2': '%s'}) == {'a_1': 'first',
                                                             'a_2': 'a'}


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


def test_map_values():
    assert map_values({'a': 'first'}) == ['first']
    assert map_values({'a': 'first', 'b': 'second'}) == ['first', 'second']


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


def test_to_kv():
    assert to_kv(1) == [{'key': '', 'value': 1}]
    assert to_kv(['a']) == [{'key': '0', 'value': 'a'}]
    assert to_kv(['a', 'b']) == [{'key': '0', 'value': 'a'},
                                 {'key': '1', 'value': 'b'}]
    assert to_kv(1, prefix='base') == [{'key': 'base', 'value': 1}]
    assert to_kv('1', prefix='base') == [{'key': 'base', 'value': '1'}]
    assert to_kv(['a', 'b'], prefix='base') == \
        [{'key': 'base.0', 'value': 'a'}, {'key': 'base.1', 'value': 'b'}]
    assert to_kv({'a': 1}, prefix='') == [{'key': 'a', 'value': 1}]
    assert to_kv({'a': ['b', 'c']}) == \
        [{'key': 'a.0', 'value': 'b'},
         {'key': 'a.1', 'value': 'c'}]
    assert to_kv({'a': ['b', 'c']}, sep='') == \
        [{'key': 'a0', 'value': 'b'},
         {'key': 'a1', 'value': 'c'}]
    assert to_kv({'a': {'b': 'c'}, 'd': 'e'}, prefix='') == \
        [{'key': 'a.b', 'value': 'c'},
         {'key': 'd', 'value': 'e'}]
    assert to_kv({'a': {'b': 'c'}, 'd': 'e'}, sep='/', prefix='') == \
        [{'key': 'a/b', 'value': 'c'},
         {'key': 'd', 'value': 'e'}]
    assert to_kv({'a': {'b': {'c': 'd'}, 'e': 'f'}, 'g': 'h'}, sep='/') == \
        [{'key': 'a/b/c', 'value': 'd'},
         {'key': 'a/e', 'value': 'f'},
         {'key': 'g', 'value': 'h'}]
    assert to_kv({'a': {'b': 'c'}, 'd': ['e', 'f']}, prefix='') == \
        [{'key': 'a.b', 'value': 'c'},
         {'key': 'd.0', 'value': 'e'},
         {'key': 'd.1', 'value': 'f'}]
    assert to_kv({'a': [{'b': 'c', 'd': 'e'}, 'h']}, sep='/', prefix='') == \
        [{'key': 'a/0/b', 'value': 'c'},
         {'key': 'a/0/d', 'value': 'e'},
         {'key': 'a/1', 'value': 'h'}]


def test_to_safe_yaml():
    assert to_safe_yaml([{'a': 0}, {'b': 1}]) == '- a: 0\n- b: 1\n'
    assert to_safe_yaml({'a': 0}) == 'a: 0\n'
    assert to_safe_yaml({'a': [0, 1]}) == 'a:\n- 0\n- 1\n'
    assert to_safe_yaml({'a': 0, 'b': 1}) == 'a: 0\nb: 1\n'
