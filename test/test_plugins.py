import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'filter_plugins'))
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'test_plugins'))

print(sys.path)

from custom_filters import reverse_record, filename, with_ext, \
    alias_keys, merge_dicts, merge_dicts_reverse, select_attributes, \
    map_format, map_format_attr, mergekd, dict2list  # noqa: E402
from custom_tests import test_network, test_property  # noqa: E402


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


def test_map_format():
    assert map_format('', '%sx') == 'x'
    assert map_format('a', '%sx') == 'ax'
    assert map_format('a', 'x%s') == 'xa'
    assert map_format('a', '%s') == 'a'
    assert map_format('a', '') == ''


def test_map_format_attr():
    d = {
        'a': 'first',
        'b': 'second'
    }
    assert map_format_attr(d, 'a', '') == {'a': '', 'b': 'second'}
    assert map_format_attr(d, 'a', '%s') == d
    assert map_format_attr(d, 'a', '%sx') == {'a': 'firstx', 'b': 'second'}
    assert map_format_attr(d, 'a', 'x%s') == {'a': 'xfirst', 'b': 'second'}
    assert map_format_attr(d, 'b', '') == {'a': 'first', 'b': ''}
    assert map_format_attr(d, 'b', '%s') == d
    assert map_format_attr(d, 'b', '%sx') == {'a': 'first', 'b': 'secondx'}
    assert map_format_attr(d, 'b', 'x%s') == {'a': 'first', 'b': 'xsecond'}
    assert map_format_attr(d, 'c', '') == d
    assert map_format_attr(d, 'c', '%s') == d
    assert map_format_attr(d, 'c', '%sx') == d
    assert map_format_attr(d, 'c', 'x%s') == d


def test_mergekd():
    d = {
        'a': 'first'
    }
    assert mergekd(['second', d], 'b') == {'a': 'first', 'b': 'second'}
    assert mergekd(['second', {}], 'b') == {'b': 'second'}
    assert mergekd(['second', d], 'a') == {'a': 'second'}


def test_dict2list():
    d = {
        'a': {
            'content': 'first'
        },
        'b': {
            'content': 'second'
        }
    }
    assert dict2list(d, 'key') == [{'key': 'a', 'content': 'first'},
                                   {'key': 'b', 'content': 'second'}]
