##########################################################################################
# pdsparser._fast_dict.py
##########################################################################################

import datetime as dt
import julian
import numbers
import re

from .utils import _based_int, _is_identifier, _format_float, _unique_key, _unwrap

_UNITS = re.compile(r' *(<.*?>)')
_BASED_INT = re.compile(r'(\d+)#(\w+)#')
_DATE = re.compile(r'"?(\d\d\d\d-\d\d(?:\d|-\d\d))"?')
_TIME = re.compile(r'"?(\d\d:\d\d(?:|\:\d\d(?:|.\d*))Z?)"?')
_DATE_TIME = re.compile(r'"?(\d\d\d\d-\d\d(?:\d|-\d\d)T\d\d:\d\d(?:|\:\d\d(|.\d*))Z?)"?')


def _clean_lines(lines):
    """Return a cleaned list of strings.

    Remove comments and blank lines; merge extended lists and strings into a single line.
    """

    cleaned = []
    prefix = ''
    quoted = False
    parens = 0
    braces = 0
    for recno, line in enumerate(lines):
        if not quoted:
            line = line.partition('/*')[0]      # strip trailing comments
        line = line.rstrip()
        text = line

        # If we are currently inside a quoted string...
        if quoted:
            quote_count = len([c for c in line if c == '"'])
            if quote_count % 2:     # if odd
                line = prefix + '\n' + text
                prefix = ''
                quoted = False
                cleaned.append((recno + 1, prefix + line))
                continue
            else:
                prefix += '\n' + text
                continue

        # Check for an unbalanced quote
        else:
            quote_count = len([c for c in line if c == '"'])
            if quote_count % 2:     # if odd
                prefix = line
                quoted = True
                continue

        line = line.lstrip()
        if not line:
            continue
        if line.startswith('/*'):
            continue
        if line == 'END':
            cleaned.append((recno + 1, 'END'))
            break

        # Balance parentheses
        if parens or braces:
            prefix = prefix + ' ' + line
            parens += len(line.split('(')) - len(line.split(')'))
            braces += len(line.split('{')) - len(line.split('}'))
            line = ''
            if parens or braces:
                continue
        else:
            parens = len(line.split('(')) - len(line.split(')'))
            braces = len(line.split('{')) - len(line.split('}'))
            if parens or braces or line[-1:] in {',', '='}:
                prefix = line
                continue

        # Otherwise, this line is complete
        cleaned.append((recno + 1, prefix + line))
        prefix = ''

    if prefix:
        raise SyntaxError('unbalanced quotes')

    return cleaned


def _evaluate(value, recno, name):
    """Evaluate one PDS3-compliant value. Lists and sets are supported."""

    value = value.strip()
    source = value
    info = {'type': None, 'source': value}
    if not value:
        return ('', info)

    is_pointer = name.startswith('^')

    if match := _DATE_TIME.fullmatch(source):
        day, sec = julian.day_sec_from_iso(match.group(1))
        order = 'YDT' if len(value.split('-')) == 2 else 'YMDT'
        hour, minute, second = julian.hms_from_sec(sec)
        isec = int(second // 1.)
        frac = second - isec
        microsec = int(1000000 * frac + 0.499999)
        digits = (-1 if isinstance(second, numbers.Integral)
                  else 6 if microsec % 1000 else 3)
        value = dt.datetime(*julian.ymd_from_day(day), hour, minute, isec, microsec)
        info['day'] = day
        info['sec'] = sec
        info['fmt'] = julian.format_day_sec(day, sec, order, digits=digits)
        info['type'] = 'date_time'
        info['source'] = match.group(1)
        return (value, info)

    if match := _DATE.fullmatch(source):
        day = julian.day_from_iso(match.group(1))
        order = 'YD' if len(value.split('-')) == 2 else 'YMD'
        value = dt.date(*julian.ymd_from_day(day))
        info['day'] = day
        info['fmt'] = julian.format_day(day, order)
        info['type'] = 'date'
        info['source'] = match.group(1)
        return (value, info)

    if match := _TIME.fullmatch(source):
        sec = julian.sec_from_iso(match.group(1).rstrip('Z'))
        info['sec'] = sec
        hour, minute, second = julian.hms_from_sec(sec)
        isec = int(second // 1.)
        frac = second - isec
        microsec = int(1000000 * frac + 0.499999)
        digits = (-1 if isinstance(second, numbers.Integral)
                  else 6 if microsec % 1000 else 3)
        value = dt.time(hour, minute, isec, microsec)
        info['type'] = 'utc_time' if match.group(1).endswith('Z') else 'local_time'
        info['fmt'] = julian.format_sec(sec, digits=digits)
        info['source'] = match.group(1)
        return (value, info)

    if match := _BASED_INT.fullmatch(value):
        radix = int(match.group(1))
        digits = match.group(2)
        value = _based_int(radix, digits)
        info['radix'] = radix
        info['digits'] = digits
        info['fmt'] = str(radix) + '#' + digits + '#'
        info['type'] = 'based_integer'
        return (value, info)

    # Handle a quoted string
    if value[0] in ('"', "'"):
        quote = value[0]
        value = value[1:-1]
        unwrap = _unwrap(value)
        if '\n' in value:
            lines = value.split('\n')
            merged = '\n'.join(line.rstrip() for line in lines[:-1]) + '\n' + lines[-1]
        if '\n' in value.strip():
            value = merged
            info['unwrap'] = unwrap
            info['source'] = quote + merged + quote
        else:
            value = unwrap
            info['source'] = source
        info['quote'] = quote
        info['type'] = ('file_pointer' if is_pointer
                        else 'quoted_text' if quote == '"' else 'quoted_symbol')
        if is_pointer:
            info['fmt'] = '"' + value + '"'
        return (value, info)

    # Extract units
    parts = _UNITS.split(value)     # odd-indexed items are units
    units = parts[1::2]
    unique_units = set(units)
    if len(unique_units) == 1:
        info['unit'] = unique_units.pop()
        value = ' '.join(parts[::2])
        # Strip extraneous whitespace from source
        parts[1::2] = [' ' + part for part in parts[1::2]]
        info['source'] = ''.join(parts)
    elif len(unique_units) > 1:
        raise SyntaxError(f'mixture of units encountered at {name}, line {recno}: '
                          f'{unique_units}')

    # Handle a sequence or set
    if source[0] in '({':

        # Identify quotes if any
        if '"' in source:
            info['quote'] = '"'
        elif "'" in source:
            info['quote'] = "'"

        # Convert to list of strings; strip whitespace
        items = [v.strip() for v in source[1:-1].split(',')]
        is_2d = any(v.startswith('(') for v in items)

        # Infer value; regenerate source without extraneous whitespace
        value = [[]]
        sources = []
        for item in items:
            ended = False
            if item.startswith('('):
                value.append([])
                sources.append('(')
                item = item[1:]
            if item.endswith(')'):
                ended = True
                item = item[:-1]

            item, local_info = _evaluate(item, recno, name)
            value[-1].append(item)
            sources.append(local_info['source'])
            sources.append('), ' if ended else ', ')

        sources[-1] = sources[-1][:-2]   # remove trailing ", "

        if is_2d:
            value = value[1:]   # first item is []
            info['source'] = '(' + ''.join(sources) + ')'
        else:
            value = value[0]    # only first item was modified
            info['source'] = source[0] + ''.join(sources) + source[-1]

        if source[0] == '{':
            info['list'] = value
            value = set(value)

        # Infer type
        if is_2d:
            info['type'] = 'sequence_2D'
        elif isinstance(value, set):
            info['type'] = 'set_pointer' if is_pointer else 'set'
        elif not is_pointer:
            info['type'] = 'sequence_1D'
        elif isinstance(value[-1], int):
            info['type'] = 'file_offset_pointer'
            info['offset'] = value[1]
            unit = info.get('unit', '')
            info['unit'] = unit.upper()
            value = value[0]
            if unit:
                info['source'] = ('("' + value + '", ' + str(info['offset'])
                                  + ' ' + unit + ')')
                info['fmt'] = ('("' + value + '", ' + str(info['offset'])
                               + ' ' + unit.upper() + ')')
            else:
                info['source'] = '("' + value + '", ' + str(info['offset']) + ')'
                info['fmt'] = info['source']
        else:
            info['type'] = 'sequence_pointer'

        return (value, info)

    # Evaluate. We take advantage of the fact that most PDS3-compliant values are also
    # Python-compliant.
    try:
        value = eval(value)
    except Exception:   # if it can't be evaluated, it may be an identifier
        info['quote'] = ''
        info['type'] = 'identifier'

    if isinstance(value, int):
        if is_pointer:
            info['type'] = 'offset_pointer'
            info['unit'] = info.get('unit', '').upper()
            info['fmt'] = str(value) + (' ' + info['unit'] if info['unit'] else '')
        else:
            info['type'] = 'integer'
    elif isinstance(value, float):
        info['type'] = 'real'

    return (value, info)


def _to_dict(lines, types=False, sources=False):
    """The dictionary from a "cleaned" list of records."""

    removals = {'quote'}
    if not types:
        removals.add('type')
    if not sources:
        removals.add('source')

    state = [('', '', {})]   # list of (OBJECT or GROUP, name, dict)
    object_keys = [[]]
    group_keys = [[]]
    statements = []
    for recno, line in lines:

        line = line.strip()
        if line == 'END':
            break

        # Get the name and value
        (name, equal, value) = line.partition('=')
        if not equal and name not in {'END_OBJECT', 'END_GROUP'}:
            raise SyntaxError(f'missing "=" at {name}, line {recno}')

        name = name.strip()
        value, info = _evaluate(value, recno, name)
        statements.append((name, value))
        for removal in removals:
            if removal in info:
                del info[removal]

        # If this begins an object, append it to the state list
        if name in ('OBJECT', 'GROUP'):
            dict_ = {name: value}
            for suffix, extra_value in info.items():
                dict_[name + '_' + suffix] = extra_value

            state.append((name, value, dict_))
            object_keys.append([])
            group_keys.append([])

        # If this ends an object, add this sub-dictionary to the dictionary
        elif name in {'END_OBJECT', 'END_GROUP'}:
            if not state:
                raise ValueError(f'unmatched {name} = {value} at line {recno}')

            (obj_type, obj_name, obj_dict) = state.pop()
            if obj_type != name[4:] or (value and value != obj_name):
                raise SyntaxError(f'unbalanced {obj_type} = {obj_name} at line {recno}')

            if not value:       # tolerate END_OBJECT or END_GROUP without name
                key = name[4:]
                obj_dict[name] = obj_dict[key]
                if 'type' not in removals:
                    obj_dict[name + '_type'] = obj_dict[key + '_type']
                if 'source' not in removals:
                    obj_dict[name + '_source'] = ''
            else:
                obj_dict[name] = value
                for suffix, extra_value in info.items():
                    obj_dict[name + '_' + suffix] = extra_value

            objects = object_keys.pop()
            if objects:
                obj_dict['objects'] = objects
            groups = group_keys.pop()
            if groups:
                obj_dict['groups'] = groups

            dict_ = state[-1][-1]
            if obj_name in {'COLUMN', 'FIELD', 'BIT_COLUMN'} and 'NAME' in obj_dict:
                obj_name = obj_dict['NAME']
            key = _unique_key(obj_name, dict_)
            dict_[key] = obj_dict
            if name == 'END_OBJECT':
                object_keys[-1].append(key)
            else:
                group_keys[-1].append(key)

        # Otherwise, interpret an attribute value
        else:
            strval = info['fmt'] if 'fmt' in info else _format(value, info)
            statements[-1] = (name, strval)

            dict_ = state[-1][-1]
            name = _unique_key(name, dict_)
            dict_[name] = value
            for suffix, extra_value in info.items():
                dict_[name + '_' + suffix] = extra_value

    # Make sure all objects and groups were terminated
    (obj_type, obj_name, obj_dict) = state.pop()
    if len(state) > 1:
        raise SyntaxError(f'unbalanced {obj_type} = {obj_name} at line {recno}')

    obj_dict['END'] = ''
    if object_keys[-1]:
        obj_dict['objects'] = object_keys[-1]
    if group_keys[-1]:
        obj_dict['groups'] = group_keys[-1]

    statements.append(('END', ''))
    return obj_dict, statements


def _format(value, info):

    if 'offset' in info:
        return ('("' + value + '", ' + str(info['offset']) +
                (' <BYTES>)' if info['unit'] else ')'))

    if isinstance(value, list):
        info = info.copy()
        info['always_quote'] = True
        return '(' + ', '.join(_format(v, info) for v in value) + ')'

    if isinstance(value, set):
        info = info.copy()
        value = info['list']
        info['always_quote'] = True
        return '{' + ', '.join(_format(v, info) for v in value) + '}'

    if isinstance(value, str):
        quote = info.get('quote', '')
        if quote:
            return quote + value + quote
        if info.get('always_quote', False):
            return '"' + value + '"'
        if _is_identifier(value):
            return value
        if value == 'N/A':
            return "'N/A'"
        return '"' + value + '"'

    unit = info.get('unit', None)
    if unit:
        temp = info.copy()
        del temp['unit']
        return _format(value, temp) + ' ' + unit
    if isinstance(value, float):
        return _format_float(value)
    if value is None:
        return None

    return str(value)


def _fast_dict(content, types=False, sources=False):
    """A hierarchical dictionary containing the content of a PDS3 label.

    This is _MUCH_ faster than pdsparser.PdsLabel.from_file (about 30x). However it does
    almost no syntax checking and may not work on some labels that are otherwise PDS3
    compliant.

    Parameters:
        content (str): The content of a PDS3 label.
        types (bool, optional): True to include PDS3 type information in the dictionary.
        sources (bool, optional): True to include the un-parsed value substrings in the
            label.
    """

    # Active code starts here

    lines = content.split('\n')
    cleaned = _clean_lines(lines)
    return _to_dict(cleaned, types=types, sources=sources)

##########################################################################################
