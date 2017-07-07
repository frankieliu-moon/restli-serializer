import urllib
import urllib2


def flatten_dict(input_dict):
    result = {}
    for key, value in input_dict.iteritems():
        if isinstance(value, dict):
            flat_value = flatten_dict(value)
            for k, v in flat_value.iteritems():
                result[key + '.' + k] = v
        elif isinstance(value, list):
            flat_value = flatten_list(value)
            for k, v in flat_value.iteritems():
                result[key + k] = v
        else:
            result[key] = value
    return result


def flatten_list(input_list):
    result = {}
    for index, item in enumerate(input_list):
        prefix = '[' + str(index) + ']'
        if isinstance(item, list):
            data = flatten_list(item)
            for key, value in data.iteritems():
                result[prefix + key] = value
        elif isinstance(item, dict):
            data = flatten_dict(item)
            for key, value in data.iteritems():
                result[prefix + '.' + key] = value
        else:
            result[prefix] = item
    return result


def get_typed_value(val, unquote):
    if unquote:
        val = urllib2.unquote(val)
    try:
        return float(val)
    except ValueError:
        pass
    if val == 'true':
        return True
    elif val == 'false':
        return False
    return val


def get_quoted_value(val, quote=True):
    if isinstance(val, bool):
        return str(val).lower()
    else:
        return urllib.quote(str(val)) if quote else str(val)
