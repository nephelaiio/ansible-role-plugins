from netaddr import IPAddress, IPNetwork
import re


def test_network(record={}, net='0.0.0.0/0', prop='ansible_host'):
    if prop in record:
        if IPAddress(record[prop]) in IPNetwork(net):
            return record


def test_property(record={}, regex='.*', prop=''):
    if prop in record:
        if re.match(regex, record[prop]):
            return record


class TestModule(object):
    ''' jinja2 filters '''

    def tests(self):
        return {
            'test_network': test_network,
            'test_property': test_property
        }
