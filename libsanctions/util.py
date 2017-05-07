from normality import stringify
from collections import OrderedDict
from hashlib import sha1


def remove_namespace(doc, namespace):
    """Remove namespace in the passed document in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]


def make_uid(*args):
    uid = sha1()
    for arg in args:
        arg = stringify(arg)
        if arg is not None:
            uid.update(arg.encode('utf-8'))
    return uid.hexdigest()


def clean_obj(data):
    """Remove empty items from JSON output."""
    if isinstance(data, (dict, OrderedDict)):
        out = {}
        for key, value in data.items():
            value = clean_obj(value)
            if value is None:
                continue
            out[key] = value
        return out
    elif isinstance(data, (list, set, tuple)):
        out = [clean_obj(d) for d in data]
        out = [o for o in out if o is not None]
        if not len(out):
            return None
        return out
    return data
