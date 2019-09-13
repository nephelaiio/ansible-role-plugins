from jinja2.utils import soft_unicode
import copy


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def merge_dicts_reverse(x, y):
    return merge_dicts(y, x)


def filename(basename):
    return (basename.split('.')[0])


def map_format(value, pattern):
    """
    Apply python string formatting on an object:
    .. sourcecode:: jinja
        {{ "%s - %s"|format("Hello?", "Foo!") }}
            -> Hello? - Foo!
    """
    if pattern != '':
        result = soft_unicode(pattern) % (value)
    else:
        result = ''
    return result


def map_format_attr(d, attr, pattern):
    """
    Apply python string formatting on an object:
    .. sourcecode:: jinja
        {{ "%s - %s"|format("Hello?", "Foo!") }}
            -> Hello? - Foo!
    """
    new_dict = copy.deepcopy(d)
    if attr in d:
        new_dict[attr] = map_format(d[attr], pattern)
    return new_dict


def reverse_record(record):
    def reverse_address(addr):
        rev = '.'.join(addr.split('.')[::-1])
        return("{0}.{1}".format(rev, 'in-addr.arpa'))
    return ({
        'host': reverse_address(record['ip-address']),
        'ip-address': record['host'],
        'type': 'PTR'
    })


def with_ext(basename, ext):
    return ("{0}.{1}".format(filename(basename), ext))


def zone_fwd(zone, servers):
    return({
        'zone "{0}" IN'.format(zone): {
            'type': 'forward',
            'forward': 'only',
            'forwarders': servers
        }
    })


def head(x):
    return(x[0])


def tail(x):
    return(x[1::])


def split_with(x, d):
    return(x.split(d))


def join_with(x, d):
    return d.join(x)


def alias_keys(d, alias={}):
    new_dict = copy.deepcopy(d)
    for k, v in list(alias.items()):
        new_dict[v] = new_dict[k]
    return new_dict


def select_attributes(d, atts):
    new_dict = {}
    for k, v in list(d.items()):
        if k in atts:
            new_dict[k] = d[k]
    return new_dict


class FilterModule(object):
    ''' jinja2 filters '''

    def filters(self):
        return {
            'split_with': split_with,
            'join_with': join_with,
            'head': head,
            'tail': tail,
            'map_format': map_format,
            'reverse_record': reverse_record,
            'zone_fwd': zone_fwd,
            'alias_keys': alias_keys,
            'merge_dicts': merge_dicts,
            'select_attributes': select_attributes,
            'merge_dicts_reverse': merge_dicts_reverse,
            'map_format_attr': map_format_attr
        }
