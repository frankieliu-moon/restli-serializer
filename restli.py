import urllib
import urllib2
from utils import flatten_dict, get_quoted_value, get_typed_value


RESTLI_V1 = '1.0.0'
RESTLI_V2 = '2.0.0'
DEFAULT_MASKS = ['fields', 'metadataFields']


class RestliSerializer(object):
    """
        A utility class that can serialize and parse restli request parameters.
    """
    
    def __init__(self, version=RESTLI_V1, mask_fields=DEFAULT_MASKS):
        """
            :param mask_fields: used only for restli v2, these are the names
                of the mask fields, a mask field specifies what attributes to
                return for each of the response objects. A default set of
                fields is used if this is not specified.
        """
        self.version = version
        self.mask_fields = DEFAULT_MASKS
    
    def serialize(self, request_params):
        if self.version == RESTLI_V1:
            return self._serialize_v1(request_params)
        else:
            return self._serialize_v2(request_params)

    def parse(self, request_string):
        if self.version == RESTLI_V1:
            return self._parse_v1(request_string)
        else:
            return self._parse_v2(request_string)

    def _serialize_v1(self, request_params):
        parameters = flatten_dict(request_params)
        key_values = []
        for key in sorted(parameters.iterkeys()):
            value = parameters[key]
            quoted_value = get_quoted_value(value, quote=True)
            key_values.append(key + '=' + quoted_value)
        return '&'.join(key_values)

    def _serialize_v2(self, request_params):
        key_values = []
        for key, value in request_params.iteritems():
            if key in self.mask_fields:
                # these are mask fields:
                sval = RestliSerializer.serialize_mask(value)
            elif isinstance(value, dict):
                sval = RestliSerializer.serialize_dict(value)
            elif isinstance(value, list):
                sval = RestliSerializer.serialize_list(value)
            else:
                sval = urllib.quote(str(value))
            key_values.append(key + '=' + sval)
        return '&'.join(key_values)

    def _parse_v1(self, request_string):
        key_values = request_string.split('&')
        request = {}
        for key_value in key_values:
            pos = str(key_value).find('=')
            if pos < 0:
                # malformed key-value pair, raise exception
                raise ValueError('Malformed query string, expecting \'=\' ..')
            keys = key_value[:pos].split('.')
            value = str(key_value[pos + 1:])
            value = get_typed_value(value, unquote=True)
            RestliSerializer.update_dict(request, keys, value)
        return request

    def _parse_v2(self, request_string):
        key_values = request_string.split('&')
        request = {}
        for key_value in key_values:
            pos = str(key_value).find('=')
            if pos < 0:
                # malformed key-value pair, raise exception
                raise ValueError('Malformed query string, expecting \'=\' ..')
            key = key_value[:pos]
            value = str(key_value[pos + 1:])
            if key == 'fields' or key == 'metadataFields':
                # this is a mask field
                request[key] = RestliSerializer.parse_mask(value)
            else:
                request[key] = RestliSerializer.parse_value(value)
        return request

    @staticmethod
    def update_dict(obj, keys, value):
        key = keys.pop(0)
        name, index = RestliSerializer.analyze_key(key)
        if index >= 0:
            # array type
            if name not in obj:
                obj[name] = []
            array = obj[name]
            while len(array) <= index:
                array.append({})
            if len(keys) == 0:
                obj[name][index] = value
                return True
            new_obj = obj[name][index]
        else:
            # dict type
            if len(keys) == 0:
                obj[name] = value
                return True
            if name not in obj:
                obj[name] = {}
            new_obj = obj[name]
        return RestliSerializer.update_dict(new_obj, keys, value)

    @staticmethod
    def analyze_key(key):
        start = key.find('[')
        if start < 0:
            # no array index
            return key, -1
        if key[-1] != ']':
            raise ValueError('Expecting ] at the end of key: ' + key)
        name = key[:start]
        index = int(key[start + 1:-1])
        return name, index

    @staticmethod
    def serialize_mask(data):
        keyvals = []
        for key, val in data.iteritems():
            if isinstance(val, dict):
                sval = RestliSerializer.serialize_mask(val)
                keyvals.append(key + ':(' + sval + ')')
            else:
                # leaf, should be just an integer 1
                keyvals.append(key)
        return ','.join(keyvals)
    
    @staticmethod
    def serialize_dict(data):
        kv = []
        for key, value in data.iteritems():
            if isinstance(value, dict):
                sval = RestliSerializer.serialize_dict(value)
            elif isinstance(value, list):
                sval = RestliSerializer.serialize_list(value)
            else:
                sval = urllib.quote(str(value))
            kv.append(key + ':' + sval)
        return '(' + ','.join(kv) + ')'
    
    @staticmethod
    def serialize_list(data):
        values = []
        for item in data:
            # usually it's a dict
            if isinstance(item, dict):
                sval = RestliSerializer.serialize_dict(item)
            elif isinstance(item, list):
                sval = RestliSerializer.serialize_list(item)
            else:
                sval = urllib.quote(str(item))
            values.append(sval)
        return 'List(' + ','.join(values) + ')'
    
    @staticmethod
    def parse_value(value):
        value = str(value)
        if value.startswith('(') and value.endswith(')'):
            # this is a map
            return RestliSerializer.parse_map(value[1:-1])
        elif value.startswith('List(') and value.endswith(')'):
            # this is a list
            return RestliSerializer.parse_list(value[5:-1])
        else:
            return urllib2.unquote(value)

    @staticmethod
    def parse_map(value):
        if len(value) == 0:
            return {}
        result = {}
        key = ''
        last_char = 0
        level = 0
        for i, c in enumerate(value):
            # c is a single character in value string
            if c == ':' and level == 0:
                key = value[last_char:i]
                last_char = i + 1
            elif c == ',' and level == 0:
                result[key] = RestliSerializer.parse_value(value[last_char:i])
                last_char = i + 1
            elif c == '(':
                level += 1
            elif c == ')':
                level -= 1
        # record the last pair
        result[key] = RestliSerializer.parse_value(value[last_char:])
        return result
    
    @staticmethod
    def parse_list(value):
        if len(value) == 0:
            return []
        level = 0
        results = []
        last_char = 0
        for i, c in enumerate(value):
            if c == '(':
                level += 1
            elif c == ')':
                level -= 1
            elif c == ',' and level == 0:
                results.append(RestliSerializer.parse_value(value[last_char:i]))
                last_char = i + 1
        # add the last element
        results.append(RestliSerializer.parse_value(value[last_char:]))
        return results
    
    @staticmethod
    def parse_mask(value):
        # algorithm is very similar to map
        result = {}
        key = None
        last_char = 0
        level = 0
        for i, c in enumerate(value):
            # c is a single character in value string
            if c == ':' and level == 0:
                key = value[last_char:i]
                last_char = i + 1
            elif c == ',' and level == 0:
                if not key:
                    result[value[last_char:i]] = 1
                else:
                    result[key] = RestliSerializer.parse_mask(value[last_char + 1:i - 1])
                last_char = i + 1
                key = None
            elif c == '(':
                level += 1
            elif c == ')':
                level -= 1
        # record the last pair
        if not key:
            result[value[last_char:]] = 1
        else:
            result[key] = RestliSerializer.parse_mask(value[last_char + 1:-1])
        return result
