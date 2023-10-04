from markupsafe import soft_str
import copy
import itertools
import yaml
import sys
import netaddr
import functools
import re

if sys.version_info[0] < 3:
    from collections import Sequence, defaultdict
else:
    from collections.abc import Sequence
    from collections import defaultdict


def is_hash(d):
    return callable(getattr(d, "get", None))


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def merge_dicts_reverse(x, y):
    return merge_dicts(y, x)


def filename(basename):
    return basename.split(".")[0]


def map_format(value, pattern):
    """
    Apply python string formatting on an object:
    .. sourcecode:: jinja
        {{ "%s - %s"|format("Hello?", "Foo!") }}
            -> Hello? - Foo!
    """
    if is_hash(value) and is_hash(pattern):

        def constant_factory(value):
            return lambda: value

        p = defaultdict(constant_factory("%s"))
        p.update(pattern)
        result = dict([[k, map_format(v, p[k])] for k, v in value.items()])
    else:
        try:
            result = soft_str(pattern) % value
        except TypeError:
            result = pattern
    return result


def map_values(d):
    return list(d.values())


def reverse_record(record):
    def reverse_address(addr):
        rev = ".".join(addr.split(".")[::-1])
        return "{0}.{1}".format(rev, "in-addr.arpa")

    return {
        "host": reverse_address(record["ip-address"]),
        "ip-address": record["host"],
        "type": "PTR",
    }


def with_ext(basename, ext):
    return "{0}.{1}".format(filename(basename), ext)


def zone_fwd(zone, servers):
    return {
        'zone "{0}" IN'.format(zone): {
            "type": "forward",
            "forward": "only",
            "forwarders": servers,
        }
    }


def head(x):
    return x[0]


def tail(x):
    return x[1::]


def split_with(x, d):
    return x.split(d)


def join_with(x, d):
    return d.join(x)


def alias_keys(d, alias={}):
    new_dict = copy.deepcopy(d)
    for k, v in list(alias.items()):
        new_dict[v] = new_dict[k]
    return new_dict


def map_attributes(d, atts):
    new_array = []
    for k in atts:
        if k in d:
            new_array = new_array + [d[k]]
    return new_array


def select_attributes(d, atts):
    new_dict = {}
    for k, v in list(d.items()):
        if k in atts:
            new_dict[k] = d[k]
    return new_dict


def drop_attributes(d, x):
    new_dict = copy.deepcopy(d)
    for y in list(itertools.chain.from_iterable([x])):
        if y in d:
            del new_dict[y]
    return new_dict


def to_dict(x, key=None):
    if key is None:
        result = dict(x)
    else:
        if is_hash(key):
            result = dict(
                [[map_format(x, k), map_format(x, v)] for k, v in key.items()]
            )
        else:
            result = {key: x}
    return result


def merge_item(item, key_attr):
    return dict(merge_dicts(item[1], to_dict(item[0], key_attr)))


def key_item(item, key_attr, remove_key=True):
    new_item = copy.deepcopy(item)
    if remove_key:
        del new_item[key_attr]
    return [item[key_attr], new_item]


def dict_to_list(d, key_attr):
    return [merge_item(item, key_attr) for item in d.items()]


def list_to_dict(l, key_attr, remove_key=True):
    return dict([key_item(x, key_attr, remove_key) for x in l])


def to_kv(d, sep=".", prefix=""):
    if is_hash(d):
        lvl = [
            to_kv(v, sep, (prefix != "" and (prefix + sep) or "") + k)
            for k, v in d.items()
        ]
        return list(itertools.chain.from_iterable(lvl))
    elif isinstance(d, Sequence) and not isinstance(d, str):
        lvl = [
            to_kv(v, sep, (prefix != "" and (prefix + sep) or "") + str(i))
            for i, v in list(enumerate(d))
        ]
        return list(itertools.chain.from_iterable(lvl))
    else:
        return [{"key": prefix, "value": d}]


def to_safe_yaml(ds, indent=2):
    return yaml.safe_dump(ds)


def sorted_get(d, ks):
    for k in ks:
        if k in d:
            return d[k]
    raise KeyError("None of {} keys found".format(ks))


def ip_range(spec):
    addrs = spec.split("-")
    start = addrs[0]
    end = start if len(addrs) == 1 else addrs[1]
    return [str(ip) for ip in netaddr.iter_iprange(start, end)]


def map_flatten(o, env=""):
    if env == "" and not isinstance(o, dict):
        raise ValueError("Argument must be dictionary")
    else:
        if isinstance(o, dict):
            flattened = {}
            for k, v in o.items():
                if env == "":
                    newenv = k
                else:
                    newenv = f"{env}.{k}"
                if isinstance(v, dict) or isinstance(v, list):
                    item = map_flatten(v, newenv)
                else:
                    item = {newenv: v}
                flattened = {**flattened, **item}
            return flattened
        elif isinstance(o, list):
            flattened = {}
            for i in range(len(o)):
                if env == "":
                    newenv = f"{i}"
                else:
                    newenv = f"{env}.{i}"
                if isinstance(o[i], dict) or isinstance(o[i], list):
                    item = map_flatten(o[i], newenv)
                else:
                    item = {newenv: o[i]}
                flattened = {**flattened, **item}
            return flattened
        else:
            return o


def map_join(d, atts, sep=" "):
    return sep.join([str(x) for x in map_attributes(d, atts)])


def merge_join(d, attr, atts, sep=" "):
    item = {
        attr: map_join(d, atts, sep),
    }
    return {**d, **item}


def map_group(l, key_atts, group_att=None):
    data_field = group_att or "data"
    groups = {}
    for x in l:
        _key = tuple(map_attributes(x, key_atts))
        if _key in groups:
            cur_item = groups[_key]
            cur_data = cur_item[data_field]
        else:
            cur_item = {}
            cur_data = []
        group_atts = select_attributes(x, key_atts)
        if group_att is None:
            groups[_key] = {
                **cur_item,
                **group_atts,
                **{data_field: cur_data + [drop_attributes(x, key_atts)]},
            }
        else:
            if group_att in x:
                groups[_key] = {
                    **cur_item,
                    **group_atts,
                    **{data_field: cur_data + [x[group_att]]},
                }
    return list(groups.values())


def is_any_true(xs):
    return functools.reduce(lambda x, y: x or y, map(lambda x: bool(x), xs), False)


def is_all_true(xs):
    return functools.reduce(lambda x, y: x and y, map(lambda x: bool(x), xs), True)


def search_regex(r, s):
    return bool(re.match(r, s))


class FilterModule(object):
    """jinja2 filters"""

    def filters(self):
        return {
            "split_with": split_with,
            "join_with": join_with,
            "head": head,
            "tail": tail,
            "map_format": map_format,
            "map_values": map_values,
            "reverse_record": reverse_record,
            "zone_fwd": zone_fwd,
            "alias_keys": alias_keys,
            "merge_dicts": merge_dicts,
            "map_attributes": map_attributes,
            "drop_attributes": drop_attributes,
            "select_attributes": select_attributes,
            "merge_dicts_reverse": merge_dicts_reverse,
            "to_dict": to_dict,
            "merge_item": merge_item,
            "key_item": key_item,
            "dict_to_list": dict_to_list,
            "list_to_dict": list_to_dict,
            "to_kv": to_kv,
            "to_safe_yaml": to_safe_yaml,
            "sorted_get": sorted_get,
            "ip_range": ip_range,
            "map_flatten": map_flatten,
            "map_join": map_join,
            "merge_join": merge_join,
            "map_group": map_group,
            "is_any_true": is_any_true,
            "is_all_true": is_all_true,
            "search_regex": search_regex,
        }
