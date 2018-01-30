import sys
import os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'filter_plugins'))
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),
                             'test_plugins'))

print(sys.path)

from custom_filters import reverse_record, filename, with_ext  # noqa: E402
from custom_tests import test_network  # noqa: E402


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
