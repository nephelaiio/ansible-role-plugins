from netaddr import IPAddress, IPNetwork


def test_network(record={}, net='0.0.0.0/0', prop='ansible_host'):
    if prop in record:
        if IPAddress(record[prop]) in IPNetwork(net):
            return record


class TestModule(object):
    ''' jinja2 filters '''

    def tests(self):
        return {
            'test_network': test_network
        }
