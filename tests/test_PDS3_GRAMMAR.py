##########################################################################################
# pdsparser/test_PDS3_GRAMMAR.py
##########################################################################################

import datetime as dt

import pytest
from pyparsing import ParseException, StringEnd

from pdsparser._PDS3_GRAMMAR import (_Integer,
                                     _BasedInteger,
                                     _Real,
                                     _NumberWithUnit,
                                     _Time,
                                     _HmsTime,
                                     _UtcTime,
                                     _TimeZone,
                                     _ZonedTime,
                                     _Date,
                                     _DateTime,
                                     _Text,
                                     _Set,
                                     _Sequence,
                                     _Sequence2D,
                                     _SimplePointer,
                                     _LocalPointer,
                                     _OffsetPointer,
                                     _SetPointer,
                                     _SequencePointer,
                                     _AttributeID,
                                     _PointerID,
                                     _Statement,
                                     _EndStatement)


def tz(minutes):
    return dt.timezone(dt.timedelta(seconds=60 * minutes))


def _grammars(cls, test):
    """The grammars of this class selected by `test`.

    If test is 1, use grammar; if test is 2, use alt_grammar; if test is 3, use both (if
    they both exist).
    """

    grammars = [cls.grammar] if (test & 1) else []
    if (test & 2) and 'alt_grammar' in cls.__dict__:
        grammars.append(cls.alt_grammar)

    if not grammars:
        raise ValueError(f'no grammar selected: {cls}, test={test}')

    return grammars


def _pass(type_, string, value, strval=None, vtype=None, test=3, super_=True):
    """Test grammar(s) for success, using parsers for this class and all superclasses.

    Returns the object parsed by the last grammar tested.
    """

    for cls in type_.__mro__:
        if not hasattr(cls, 'grammar'):
            break

        for grammar in _grammars(cls, test):
            obj = (grammar + StringEnd()).parse_string(string)[0]

            assert isinstance(obj, type_)
            assert obj.value == value

            if vtype:
                assert isinstance(obj.value, vtype)

            if strval:
                assert str(obj) == strval

        if not super_:
            break

    return obj


def _fail(type_, string, test=3, super_=True):
    """Test grammar(s) for failure, using parsers for this class and all superclasses."""

    for cls in type_.__mro__:
        if not hasattr(cls, 'grammar'):
            break

        for grammar in _grammars(cls, test):
            with pytest.raises(ParseException):
                (grammar + StringEnd()).parse_string(string)

        if not super_:
            break


##########################################################################################
# _Integer
##########################################################################################

def test_integer_attributes():

    obj = _pass(_Integer, '123', 123)
    assert obj.type_ == 'integer'
    assert obj.value == 123
    assert obj.full_value == 123
    assert str(obj) == '123'
    assert repr(obj) == '_Integer(123)'
    assert obj == 123


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('-123', -123, None),
    ('+123', 123, '123'),
])
def test_integer_parses(string, value, strval):
    _pass(_Integer, string, value, strval)


@pytest.mark.parametrize('string', ['+ 123', '- 123'])
def test_integer_rejects(string):
    _fail(_Integer, string)


##########################################################################################
# _BasedInteger
##########################################################################################

def test_based_integer_attributes():

    obj = _pass(_BasedInteger, '2#11111111#', 255, '2#11111111#', int)
    assert str(obj) == '2#11111111#'
    assert repr(obj) == '_BasedInteger(2#11111111#)'
    assert obj == 255
    assert obj.radix == 2
    assert obj.digits == '11111111'
    assert obj.fmt == '2#11111111#'


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('2#000011111111#', 255, '2#000011111111#'),
    ('8#7#', 7, None),
    ('8#10#', 8, None),
    ('8#100#', 64, None),
    ('8#1000#', 512, None),
    ('8#10000#', 4096, None),
    ('16#FF#', 255, None),
])
def test_based_integer_parses(string, value, strval):
    _pass(_BasedInteger, string, value, strval)


@pytest.mark.parametrize('string', ['1#000#', '7#1#', '3#123#', '8# 123#', '8 #123#',
                                    '8#123 #'])
def test_based_integer_rejects(string):
    _fail(_BasedInteger, string)


##########################################################################################
# _Real
##########################################################################################

def test_real_attributes():

    obj = _pass(_Real, '123.', 123., '123.', float)
    assert obj.type_ == 'real'
    assert str(obj) == '123.'
    assert repr(obj) == '_Real(123.)'
    assert obj == 123


@pytest.mark.parametrize(('string', 'value', 'strval', 'vtype'), [
    ('1234.5', 1234.5, '1234.5', None),
    ('+1234.5', 1234.5, '1234.5', None),
    ('-1234.5', -1234.5, '-1234.5', None),
    ('1234.5e6', 1234500000., '1234500000.', float),
    ('1234.5e006', 1234500000., None, None),
    ('1234.5e+006', 1234500000., None, None),
    ('1234.5e-006', 0.0012345, None, None),
    ('.5e+2', 50, '50.', float),
    ('5e+2', 500, '500.', float),
    ('-1e+20', -1.e20, '-1.e+20', None),
])
def test_real_parses(string, value, strval, vtype):
    _pass(_Real, string, value, strval, vtype)


@pytest.mark.parametrize('string', ['1234.5e0006', '1234 .5e06', '1234.5 e06',
                                    '1234.5e 06', '1234.5e+ 06'])
def test_real_rejects(string):
    _fail(_Real, string)


##########################################################################################
# _NumberWithUnit
##########################################################################################

def test_number_with_unit_attributes():

    obj = _pass(_NumberWithUnit, '123.  <km>', 123., '123. <km>', float)
    assert obj.unit == '<km>'
    assert obj.full_value == (123., '<km>')
    assert obj.type_ == 'real'
    assert str(obj) == '123. <km>'
    assert repr(obj) == '_NumberWithUnit(123. <km>)'
    assert obj.value == 123.


def test_number_with_unit_spaces_in_unit():

    obj = _pass(_NumberWithUnit, '-1234.5 < km/s>', -1234.5, '-1234.5 <km/s>')
    assert obj.unit == '<km/s>'
    assert obj.full_value == (-1234.5, '<km/s>')

    obj = _pass(_NumberWithUnit, '+1 < local day >', 1, '1 <local day>', int)
    assert obj.unit == '<local day>'


def test_number_with_unit_compares_as_number():
    assert _NumberWithUnit.grammar.parse_string('100 <km>')[0] == 100


##########################################################################################
# _HmsTime and _UtcTime
##########################################################################################

def test_hms_time_attributes():

    obj = _pass(_HmsTime, '12:34:56', dt.time(12, 34, 56))
    assert obj.type_ == 'local_time'
    assert str(obj) == '12:34:56'
    assert repr(obj) == '_HmsTime(12:34:56)'
    assert obj.sec == 56 + 60 * (34 + 60 * 12)
    assert obj.fmt == '12:34:56'
    assert type(obj.sec) is int


def test_hms_time_fractional_seconds():

    obj = _pass(_HmsTime, '12:34:56.123456', dt.time(12, 34, 56, 123456),
                strval='12:34:56.123456')
    assert obj.type_ == 'local_time'
    assert str(obj) == '12:34:56.123456'
    assert repr(obj) == '_HmsTime(12:34:56.123456)'
    assert obj.sec == 56.123456 + 60 * (34 + 60 * 12)
    assert obj.fmt == '12:34:56.123456'


@pytest.mark.parametrize(('type_', 'string', 'value', 'strval', 'type_name'), [
    (_UtcTime, '12:34:56Z', dt.time(12, 34, 56), '12:34:56', 'utc_time'),
    (_UtcTime, '12:34:56.123456Z', dt.time(12, 34, 56, 123456), '12:34:56.123456',
     'utc_time'),
    (_HmsTime, '12:34', dt.time(12, 34), '12:34:00', 'local_time'),
    (_UtcTime, '12:34Z', dt.time(12, 34), '12:34:00', 'utc_time'),
])
def test_simple_time_type(type_, string, value, strval, type_name):
    obj = _pass(type_, string, value, strval)
    assert obj.type_ == type_name


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('"12:34:56"', dt.time(12, 34, 56), None),
    ('"12:34:56.5"', dt.time(12, 34, 56, 500000), '12:34:56.500'),
    ('"12:34:56.12345678"', dt.time(12, 34, 56, 123457), '12:34:56.123457'),
    ('"01:01:01"', dt.time(1, 1, 1), None),
])
def test_hms_time_quoted(string, value, strval):
    _pass(_HmsTime, string, value, strval)


@pytest.mark.parametrize(('string', 'value', 'sec_type'), [
    ('"12:34:01"', dt.time(12, 34, 1), int),
    ('"12:34:01."', dt.time(12, 34, 1), float),
    ('"01:01"', dt.time(1, 1, 0), int),
])
def test_hms_time_leading_zeros(string, value, sec_type):
    obj = _pass(_HmsTime, string, value)
    assert isinstance(obj.sec, sec_type)


@pytest.mark.parametrize(('type_', 'string'), [
    (_HmsTime, '12:3'),
    (_HmsTime, '123:34'),
    (_HmsTime, '123 :34'),
    (_HmsTime, '123: 34'),
    (_UtcTime, '12:34 Z'),
])
def test_simple_time_rejects(type_, string):
    _fail(type_, string)


@pytest.mark.parametrize(('type_', 'string'), [
    (_HmsTime, '12:34Z'),
    (_UtcTime, '12:34'),
])
def test_simple_time_rejects_other_type(type_, string):
    _fail(type_, string, super_=False)


def test_hms_time_one_digit_hour_is_loose_only():
    _fail(_HmsTime, '2:34', test=1)
    _pass(_HmsTime, '2:34', dt.time(2, 34), '02:34:00', test=2, super_=False)


@pytest.mark.parametrize(('type_', 'string', 'value', 'strval', 'type_name'), [
    (_UtcTime, '12: 4:56Z', dt.time(12, 4, 56), '12:04:56', 'utc_time'),
    (_UtcTime, '12:34: 6.123456Z', dt.time(12, 34, 6, 123456), '12:34:06.123456',
     'utc_time'),
    (_HmsTime, ' 2:34', dt.time(2, 34), '02:34:00', 'local_time'),
    (_UtcTime, ' 2:34Z', dt.time(2, 34), '02:34:00', 'utc_time'),
    (_HmsTime, '12: 4', dt.time(12, 4), '12:04:00', 'local_time'),
    (_UtcTime, '12: 4Z', dt.time(12, 4), '12:04:00', 'utc_time'),
    (_HmsTime, '" 2:34:56"', dt.time(2, 34, 56), None, None),
    (_HmsTime, '"12: 4:56"', dt.time(12, 4, 56), None, None),
    (_HmsTime, '"12:34: 6"', dt.time(12, 34, 6), None, None),
    (_HmsTime, '"12:34: 6.5"', dt.time(12, 34, 6, 500000), '12:34:06.500', None),
])
def test_simple_time_blanks_for_zeros(type_, string, value, strval, type_name):
    obj = _pass(type_, string, value, strval, test=2, super_=False)
    if type_name:
        assert obj.type_ == type_name


##########################################################################################
# _TimeZone
##########################################################################################

@pytest.mark.parametrize(('string', 'minutes', 'strval'), [
    ('+02:30', 2*60 + 30, '+02:30'),
    ('+00:30', 30, '+00:30'),
    ('-00:30', -30, '-00:30'),
    ('+14:45', 14*60 + 45, '+14:45'),
    ('-12:45', -12*60 - 45, '-12:45'),
    ('-00', 0, '+00'),
    ('+00', 0, '+00'),
    ('-01', -60, '-01'),
    ('+01', 60, '+01'),
    ('-1:15', -75, '-01:15'),
    ('-0', 0, '+00'),
    ('-1', -60, '-01'),
    ('+0', 0, '+00'),
    ('+1', 60, '+01'),
])
def test_time_zone_parses(string, minutes, strval):
    _pass(_TimeZone, string, tz(minutes), strval, dt.timezone)


@pytest.mark.parametrize('string', ['0:30', '-000', ' -0:30', '-0 :30', '-0: 30', '-24',
                                    '+24', '+0:60', 'Z'])
def test_time_zone_rejects(string):
    _fail(_TimeZone, string)


@pytest.mark.parametrize(('string', 'minutes', 'strval'), [
    ('- 0:30', -30, '-00:30'),
    ('-01: 0', -60, '-01:00'),
])
def test_time_zone_blanks_are_loose_only(string, minutes, strval):
    _fail(_TimeZone, string, test=1)
    _pass(_TimeZone, string, tz(minutes), strval, test=2)


##########################################################################################
# _ZonedTime
##########################################################################################

@pytest.mark.parametrize(('string', 'minutes', 'strval', 'sec'), [
    ('12:34+2', 2*60, '12:34:00+02', 3600*12 + 34*60 - 3600*2),
    ('12:34+2:30', 2*60 + 30, '12:34:00+02:30', 3600*12 + 34*60 - 3600*2 - 30*60),
])
def test_zoned_time_attributes(string, minutes, strval, sec):

    obj = _pass(_ZonedTime, string, dt.time(12, 34, tzinfo=tz(minutes)), strval,
                super_=False)
    assert obj.type_ == 'zoned_time'
    assert obj.sec == sec
    assert obj.fmt == strval
    assert str(obj) == strval
    assert repr(obj) == f'_ZonedTime({strval})'
    assert obj.source == string


@pytest.mark.parametrize(('string', 'minutes', 'strval'), [
    ('"12:34-02"', -2*60, '12:34:00-02'),
    ('"12:34-02:45"', -2*60 - 45, '12:34:00-02:45'),
])
def test_zoned_time_quoted(string, minutes, strval):
    _pass(_ZonedTime, string, dt.time(12, 34, tzinfo=tz(minutes)), strval, super_=False)


@pytest.mark.parametrize('string', ['12:34 +2:30', '12:34 +02:30', '12:34 -2'])
def test_zoned_time_rejects(string):
    _fail(_ZonedTime, string)


def test_zoned_time_blank_in_zone_is_loose_only():
    _fail(_ZonedTime, '12:34- 2', test=1)
    _pass(_ZonedTime, '12:34- 2', dt.time(12, 34, tzinfo=tz(-2*60)), '12:34:00-02',
          test=2)


##########################################################################################
# _Time
##########################################################################################

def test_time_attributes():

    obj = _pass(_Time, '12:34:56', dt.time(12, 34, 56))
    assert obj.type_ == 'local_time'
    assert str(obj) == '12:34:56'
    assert repr(obj) == '_HmsTime(12:34:56)'
    assert obj.sec == 56 + 60 * (34 + 60 * 12)
    assert obj.fmt == '12:34:56'
    assert type(obj.sec) is int


def test_time_fractional_seconds():

    obj = _pass(_Time, '12:34:56.123456', dt.time(12, 34, 56, 123456),
                strval='12:34:56.123456')
    assert obj.type_ == 'local_time'
    assert str(obj) == '12:34:56.123456'
    assert repr(obj) == '_HmsTime(12:34:56.123456)'
    assert obj.sec == 56.123456 + 60 * (34 + 60 * 12)
    assert obj.fmt == '12:34:56.123456'


@pytest.mark.parametrize(('string', 'value', 'strval', 'type_name'), [
    ('12:34:56Z', dt.time(12, 34, 56), '12:34:56', 'utc_time'),
    ('12:34:56.123456Z', dt.time(12, 34, 56, 123456), '12:34:56.123456', 'utc_time'),
    ('12:34', dt.time(12, 34), '12:34:00', 'local_time'),
    ('12:34Z', dt.time(12, 34), '12:34:00', 'utc_time'),
])
def test_time_type(string, value, strval, type_name):
    obj = _pass(_Time, string, value, strval)
    assert obj.type_ == type_name


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('"12:34:56"', dt.time(12, 34, 56), None),
    ('"12:34:56.5"', dt.time(12, 34, 56, 500000), '12:34:56.500'),
    ('"12:34:56.12345678"', dt.time(12, 34, 56, 123457), '12:34:56.123457'),
])
def test_time_quoted(string, value, strval):
    _pass(_Time, string, value, strval)


def test_time_zoned():

    obj = _pass(_Time, '12:34+2:30', dt.time(12, 34, tzinfo=tz(2*60 + 30)),
                '12:34:00+02:30', dt.time, test=2)
    assert obj.type_ == 'zoned_time'
    assert obj.sec == 3600*12 + 34*60 - 3600*2 - 30*60
    assert obj.fmt == '12:34:00+02:30'
    assert str(obj) == '12:34:00+02:30'
    assert repr(obj) == '_ZonedTime(12:34:00+02:30)'


@pytest.mark.parametrize('string', ['12:34 +2:30', '12:34 +02:30'])
def test_time_rejects_blank_before_zone(string):
    _fail(_Time, string, test=1)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    (' 2:34:56', dt.time(2, 34, 56), '02:34:56'),
    ('12: 4:56', dt.time(12, 4, 56), '12:04:56'),
    ('12:34: 6', dt.time(12, 34, 6), '12:34:06'),
    (' 2: 4: 6Z', dt.time(2, 4, 6), '02:04:06'),
    (' 2:34:56.123456', dt.time(2, 34, 56, 123456), '02:34:56.123456'),
    ('12: 4:56.123456', dt.time(12, 4, 56, 123456), '12:04:56.123456'),
    ('12:34: 6.123456', dt.time(12, 34, 6, 123456), '12:34:06.123456'),
])
def test_time_blanks_for_zeros(string, value, strval):
    _pass(_Time, string, value, strval, test=2)


##########################################################################################
# _Date
##########################################################################################

@pytest.mark.parametrize(('string', 'value', 'day'), [
    ('2000-01-01', dt.date(2000, 1, 1), 0),
    ('2000-003', dt.date(2000, 1, 3), 2),
])
def test_date_attributes(string, value, day):

    obj = _pass(_Date, string, value)
    assert obj.type_ == 'date'
    assert obj.day == day
    assert str(obj) == string
    assert repr(obj) == f'_Date({string})'


@pytest.mark.parametrize(('string', 'value'), [
    ('2000-12-01', dt.date(2000, 12, 1)),
    ('2000-12-31', dt.date(2000, 12, 31)),
    ('2000-366', dt.date(2000, 12, 31)),
])
def test_date_parses(string, value):
    _pass(_Date, string, value)


@pytest.mark.parametrize('string', ['3000-01-01', '2000-00-01', '2000-13-01',
                                    '2000-01-00', '2000-01-32'])
def test_date_rejects(string):
    _fail(_Date, string)


@pytest.mark.parametrize('string', ['2000- 1-01', '2000-01- 1'])
def test_date_blanks_for_zeros_are_loose_only(string):
    _fail(_Date, string, test=1)
    _pass(_Date, string, dt.date(2000, 1, 1), '2000-01-01', test=2, super_=False)


##########################################################################################
# _DateTime
##########################################################################################

def test_date_time_type():
    obj = _pass(_DateTime, '2000-01-03T12:34', dt.datetime(2000, 1, 3, 12, 34),
                '2000-01-03T12:34:00', test=1)
    assert obj.type_ == 'date_time'


@pytest.mark.parametrize(('string', 'value', 'strval', 'test', 'day', 'sec'), [
    ('2000-01-03T12:34', dt.datetime(2000, 1, 3, 12, 34), '2000-01-03T12:34:00', 1,
     2, 60 * (34 + 60 * 12)),
    ('2000-003T12:34Z', dt.datetime(2000, 1, 3, 12, 34), '2000-003T12:34:00', 1,
     2, 60 * (34 + 60 * 12)),
    ('2000-01-01T01:23+4', dt.datetime(2000, 1, 1, 1, 23, tzinfo=tz(4*60)),
     '2000-01-01T01:23:00+04', 2, -1, 60 * (23 + 60) - 4 * 3600 + 86400),
    ('2000-01-01T23:46-4: 0', dt.datetime(2000, 1, 1, 23, 46, tzinfo=tz(-4*60)),
     '2000-01-01T23:46:00-04:00', 2, 1, 60 * (46 + 60 * 23) - 20 * 3600),
])
def test_date_time_attributes(string, value, strval, test, day, sec):

    obj = _pass(_DateTime, string, value, strval, test=test)
    assert obj.day == day
    assert obj.sec == sec
    assert str(obj) == strval
    assert repr(obj) == f'_DateTime({strval})'


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('2000-01-01T12:34Z', dt.datetime(2000, 1, 1, 12, 34), '2000-01-01T12:34:00'),
    ('2000-01-01T12:34:56Z', dt.datetime(2000, 1, 1, 12, 34, 56),
     '2000-01-01T12:34:56'),
    ('2004-366T04:38:16.12345678Z', dt.datetime(2004, 12, 31, 4, 38, 16, 123457),
     '2004-366T04:38:16.123457'),
])
def test_date_time_parses(string, value, strval):
    _pass(_DateTime, string, value, strval)


@pytest.mark.parametrize('string', ['2000-01-01 T12:34', '2000-01-01T 12:34',
                                    '2000-01-01T12:34 Z', '2000-01-01T12:34:56+07:08'])
def test_date_time_rejects(string):
    _fail(_DateTime, string)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('2000-01-01T01:23+4', dt.datetime(2000, 1, 1, 1, 23, tzinfo=tz(4*60)),
     '2000-01-01T01:23:00+04'),
    ('2000-01-01T12:34:56+7:15', dt.datetime(2000, 1, 1, 12, 34, 56, tzinfo=tz(7*60+15)),
     '2000-01-01T12:34:56+07:15'),
])
def test_date_time_zone_is_loose_only(string, value, strval):
    _fail(_DateTime, string, test=1)
    _pass(_DateTime, string, value, strval, test=2)


@pytest.mark.parametrize('string', ['2000- 1-01T12:34', '2000-01- 1T12:34',
                                    '2000-01- 2T12:34Z', '2000-01-01T 1:23+4',
                                    '2000-01-01T12: 4:56+7:15',
                                    '2000-01-01T12:34: 6+07:08'])
def test_date_time_strict_rejects_blanks(string):
    _fail(_DateTime, string, test=1)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('2004- 1-22T12:34', dt.datetime(2004, 1, 22, 12, 34), '2004-01-22T12:34:00'),
    ('2004-11- 2T12:34', dt.datetime(2004, 11, 2, 12, 34), '2004-11-02T12:34:00'),
    ('2004-11-22T 2:34Z', dt.datetime(2004, 11, 22, 2, 34), '2004-11-22T02:34:00'),
    ('2004-11-22T12:04', dt.datetime(2004, 11, 22, 12, 4), '2004-11-22T12:04:00'),
    ('2004-11-22T12:34: 6Z', dt.datetime(2004, 11, 22, 12, 34, 6),
     '2004-11-22T12:34:06'),
    ('2004-11-22T12:34:56+7', dt.datetime(2004, 11, 22, 12, 34, 56, tzinfo=tz(7*60)),
     '2004-11-22T12:34:56+07'),
    ('2004-11-22T12:34:56+07: 0', dt.datetime(2004, 11, 22, 12, 34, 56, tzinfo=tz(7*60)),
     '2004-11-22T12:34:56+07:00'),
])
def test_date_time_blanks_for_zeros(string, value, strval):
    _pass(_DateTime, string, value, strval, test=2)


##########################################################################################
# _Text
##########################################################################################

def test_text_identifier():

    obj = _pass(_Text, 'ABC', 'ABC', 'ABC')
    assert obj.type_ == 'identifier'
    assert str(obj) == obj.value
    assert repr(obj) == '_Text(ABC)'
    assert obj == 'ABC'


def test_text_quoted():

    obj = _pass(_Text, '"abc"', 'abc', '"abc"')
    assert obj.type_ == 'quoted_text'
    assert str(obj) == '"abc"'
    assert repr(obj) == '_Text("abc")'
    assert obj == 'abc'


def test_text_lowercase_identifier_is_loose_only():

    _fail(_Text, 'abc', test=1)
    obj = _pass(_Text, 'abc', 'abc', '"abc"', test=2)
    assert obj.type_ == 'identifier'
    assert repr(obj) == '_Text("abc")'
    assert obj == 'abc'


def test_text_quoted_symbol():

    obj = _pass(_Text, "'N/A'", 'N/A')
    assert obj.type_ == 'quoted_symbol'
    assert repr(obj) == "_Text('N/A')"
    assert obj == 'N/A'


def test_text_multiline():

    obj = _pass(_Text, '"Multiline\ntext"', 'Multiline\ntext')
    assert repr(obj) == '_Text("Multiline\ntext")'
    assert obj == 'Multiline\ntext'
    assert obj.source == '"Multiline\ntext"'
    assert obj.unwrap == 'Multiline text'


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('"abc def"', 'abc def', '"abc def"'),
    ('""', '', None),
    ('"   "', '', None),
])
def test_text_parses(string, value, strval):
    _pass(_Text, string, value, strval)


def test_text_unquoted_symbol_is_loose_only():
    _fail(_Text, 'N/A', test=1)
    _pass(_Text, 'N/A', 'N/A', "'N/A'", test=2)


def test_text_rejects_unquoted_blank():
    _fail(_Text, 'abc def')


##########################################################################################
# _Set
##########################################################################################

def test_set_attributes():

    obj = _pass(_Set, '{1, 2, \n3}', {1, 2, 3}, '{1, 2, 3}', set)
    assert obj.type_ == 'set'
    assert str(obj) == '{1, 2, 3}'
    assert repr(obj) == '_Set(1, 2, 3)'
    assert obj == {1, 2, 3}
    assert obj.list == [1, 2, 3]


def test_set_mixed_units():

    obj = _pass(_Set, '{1, 2<km>}', {1, (2, '<km>')}, '{1, 2 <km>}')
    assert (2, '<km>') in obj.full_value
    assert 2 not in obj.full_value
    assert type(obj[0]) is _Integer
    assert obj[0].value == 1
    assert type(obj[1]) is _NumberWithUnit


def test_set_common_unit():

    obj = _pass(_Set, '{1<km>, 2<km>}', {1, 2}, '{1 <km>, 2 <km>}')
    assert type(obj[0]) is _NumberWithUnit
    assert type(obj[1]) is _NumberWithUnit
    assert type(obj[0].value) is int
    assert type(obj[1].value) is int
    assert obj.unit == '<km>'


def test_set_quotes():

    obj = _pass(_Set, '{1, "abc", \'def\', GHI}', {1, "abc", "def", "GHI"},
                '{1, "abc", \'def\', "GHI"}')
    assert type(obj[1]) is _Text
    assert obj[1].value == 'abc'
    assert obj[1].quote == '"'
    assert type(obj[2]) is _Text
    assert obj[2].value == 'def'
    assert obj[2].quote == "'"
    assert type(obj[3]) is _Text
    assert obj[3].value == 'GHI'
    assert obj[3].quote == ''
    assert obj.quote == '"'


def test_set_single_quote():

    obj = _pass(_Set, '{1, \'def\', GHI}', {1, "def", "GHI"}, '{1, \'def\', "GHI"}')
    assert obj[1].quote == "'"
    assert obj[2].quote == ''
    assert obj.quote == "'"


def test_set_no_quotes():

    obj = _pass(_Set, '{1, GHI}', {1, "GHI"}, '{1, "GHI"}')
    assert obj[1].quote == ''
    assert obj.quote == ''


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('{1, 2\n,3}', {1, 2, 3}, '{1, 2, 3}'),
    ('{1, 2.0, "three"}', {1, 2.0, "three"}, '{1, 2., "three"}'),
    ('{1, 2.0, THREE}', {1, 2.0, "THREE"}, '{1, 2., "THREE"}'),
])
def test_set_parses(string, value, strval):
    _pass(_Set, string, value, strval)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('{1, 2.0, three}', {1, 2.0, "three"}, '{1, 2., "three"}'),
    ('{1, 2.0, N/A}', {1, 2.0, "N/A"}, "{1, 2., 'N/A'}"),
])
def test_set_unquoted_text_is_loose_only(string, value, strval):
    _fail(_Set, string, test=1)
    _pass(_Set, string, value, strval, test=2)


@pytest.mark.parametrize('string', ['{1, (2, 3)}', '{1, {2, 3}}'])
def test_set_rejects_nesting(string):
    _fail(_Set, string)


##########################################################################################
# _Sequence
##########################################################################################

def test_sequence_attributes():

    obj = _pass(_Sequence, '(1, 2, \n3)', [1, 2, 3], '(1, 2, 3)', list)
    assert obj.type_ == 'sequence_1D'
    assert str(obj) == '(1, 2, 3)'
    assert repr(obj) == '_Sequence(1, 2, 3)'
    assert obj == [1, 2, 3]


def test_sequence_mixed_units():

    obj = _pass(_Sequence, '(1, 2<km>)', [1, 2], '(1, 2 <km>)', list)
    assert obj[0].full_value == 1
    assert obj[1].full_value == (2, '<km>')
    assert type(obj[0].value) is int
    assert type(obj[1].value) is int
    assert obj.unit == [None, '<km>']
    assert type(obj.unit) is list
    assert obj.all_units == [None, '<km>']


def test_sequence_common_unit():

    obj = _pass(_Sequence, '(1 <km>, 2.<km>)', [1, 2.], '(1 <km>, 2. <km>)', list)
    assert obj[0].full_value == (1, '<km>')
    assert obj[1].full_value == (2., '<km>')
    assert type(obj[0].full_value[0]) is int
    assert type(obj[1].full_value[0]) is float
    assert type(obj[0].value) is int
    assert type(obj[1].value) is float
    assert obj.unit == '<km>'
    assert obj.all_units == ['<km>', '<km>']
    assert repr(obj) == '_Sequence(1 <km>, 2. <km>)'
    assert obj == [1, 2]


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('(1, 2\n,3)', [1, 2, 3], '(1, 2, 3)'),
    ('(1, 2.0, "three")', [1, 2.0, "three"], '(1, 2., "three")'),
    ('(1, 2.0, THREE)', [1, 2.0, "THREE"], '(1, 2., "THREE")'),
])
def test_sequence_parses(string, value, strval):
    _pass(_Sequence, string, value, strval)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('(1, 2.0, three)', [1, 2.0, "three"], '(1, 2., "three")'),
    ('(1, 2.0, N/A)', [1, 2.0, "N/A"], "(1, 2., 'N/A')"),
])
def test_sequence_unquoted_text_is_loose_only(string, value, strval):
    _fail(_Sequence, string, test=1)
    _pass(_Sequence, string, value, strval, test=2)


@pytest.mark.parametrize('string', ['(1, (2, 3))', '(1, {2, 3})'])
def test_sequence_rejects_nesting(string):
    _fail(_Sequence, string)


##########################################################################################
# _Sequence2D
##########################################################################################

def test_sequence_2d_one_row():

    obj = _pass(_Sequence2D, '((1, 2, 3))', [[1, 2, 3]], '((1, 2, 3))', list)
    assert obj[0].value == [1, 2, 3]
    assert type(obj[0].value) is list


def test_sequence_2d_two_rows():

    obj = _pass(_Sequence2D, '((1, 2, 3), (4,5))', [[1, 2, 3], [4, 5]],
                '((1, 2, 3), (4, 5))', list)
    assert obj[0].value == [1, 2, 3]
    assert obj[1].value == [4, 5]
    assert obj[0].full_value == [1, 2, 3]
    assert obj[1].full_value == [4, 5]
    assert obj[0][0].full_value == 1
    assert obj[1][1].full_value == 5
    assert obj.unit is None
    assert obj.all_units == [[None, None, None], [None, None]]


def test_sequence_2d_mixed_units():

    obj = _pass(_Sequence2D, '((1, 2, 3), (4,5 <km>))', [[1, 2, 3], [4, 5]],
                '((1, 2, 3), (4, 5 <km>))', list)
    assert obj[0].value == [1, 2, 3]
    assert obj[1].value == [4, 5]
    assert obj[0].full_value == [1, 2, 3]
    assert obj[1].full_value == [4, (5, '<km>')]
    assert obj[0][0].full_value == 1
    assert obj[1][1].full_value == (5, '<km>')
    assert obj.unit == [[None, None, None], [None, '<km>']]
    assert obj.all_units == [[None, None, None], [None, '<km>']]
    assert type(obj[1][1]) is _NumberWithUnit
    assert type(obj[1][1].value) is int


def test_sequence_2d_unit_in_one_row():

    obj = _pass(_Sequence2D, '((1, 2<km>))', [[1, 2]], '((1, 2 <km>))')
    assert obj[0][0].full_value == 1
    assert obj[0][1].full_value == (2., '<km>')
    assert obj[0][1].unit == '<km>'
    assert obj.unit == [[None, '<km>']]
    assert obj.all_units == [[None, '<km>']]


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('(\n(\n\t1, 2\n,3\t))', [[1, 2, 3]], '((1, 2, 3))'),
    ('((1, 2.0, "three"))', [[1, 2.0, "three"]], '((1, 2., "three"))'),
])
def test_sequence_2d_parses(string, value, strval):
    _pass(_Sequence2D, string, value, strval)


@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('((1, 2.0, three))', [[1, 2.0, "three"]], '((1, 2., "three"))'),
    ('((1,2)\n(3,4))', [[1, 2], [3, 4]], None),
])
def test_sequence_2d_loose_only(string, value, strval):
    _fail(_Sequence2D, string, test=1)
    _pass(_Sequence2D, string, value, strval, test=2)


def test_sequence_2d_strict_rejects_unquoted_symbol():
    _fail(_Sequence2D, '((1, 2.0, N/A))', test=1)


@pytest.mark.parametrize('string', ['((1, (2, 3)))', '((1, {2, 3}))'])
def test_sequence_2d_rejects_nesting(string):
    _fail(_Sequence2D, string)


##########################################################################################
# Pointers
##########################################################################################

@pytest.mark.parametrize(('string', 'value'), [
    ('"DOCUMENT.PDF"', 'DOCUMENT.PDF'),
    ('"DOC.TXT.PDF"', 'DOC.TXT.PDF'),
])
def test_simple_pointer_parses(string, value):
    _pass(_SimplePointer, string, value, string)


def test_simple_pointer_directory_is_loose_only():
    _fail(_SimplePointer, '"DIR/DOC.TXT.PDF"', test=1)
    _pass(_SimplePointer, '"DIR/DOC.TXT.PDF"', 'DIR/DOC.TXT.PDF', '"DIR/DOC.TXT.PDF"',
          test=2)


@pytest.mark.parametrize(('string', 'strval'), [
    ('123', '123'),
    ('123\t<BYTES>', '123 <BYTES>'),
    ('123<bytes>', '123 <BYTES>'),
])
def test_local_pointer_parses(string, strval):
    _pass(_LocalPointer, string, 123, strval, int)


def test_local_pointer_bytes():
    obj = _pass(_LocalPointer, '123<bytes>', 123, '123 <BYTES>', int)
    assert obj.full_value == (123, '<BYTES>')


@pytest.mark.parametrize(('string', 'strval', 'full_value', 'offset', 'unit'), [
    ('("TABLE.TAB", 2)', '("TABLE.TAB", 2)', ("TABLE.TAB", 2), 2, ''),
    ('("TABLE.TAB", 800 <bytes>)', '("TABLE.TAB", 800 <BYTES>)',
     ("TABLE.TAB", 800, '<BYTES>'), 800, '<BYTES>'),
])
def test_offset_pointer_attributes(string, strval, full_value, offset, unit):

    obj = _pass(_OffsetPointer, string, 'TABLE.TAB', strval)
    assert obj.full_value == full_value
    assert obj.offset == offset
    assert isinstance(obj.offset, int)
    assert obj.unit == unit


@pytest.mark.parametrize(('string', 'strval'), [
    ('("DIR/TABLE.TAB", 2)', '("DIR/TABLE.TAB", 2)'),
    ('("DIR/TABLE.TAB", 800 <bytes>)', '("DIR/TABLE.TAB", 800 <BYTES>)'),
])
def test_offset_pointer_directory_is_loose_only(string, strval):
    _fail(_OffsetPointer, string, test=1)
    _pass(_OffsetPointer, string, 'DIR/TABLE.TAB', strval, test=2)


@pytest.mark.parametrize('string', [
    '{"1.GIF", "2.GIF", "3.GIF"}',
    '{"1.GIF", "2.GIF", "2.GIF", "3.GIF"}',
])
def test_set_pointer_parses(string):
    _pass(_SetPointer, string, {"1.GIF", "2.GIF", "3.GIF"}, '{"1.GIF", "2.GIF", "3.GIF"}')


def test_set_pointer_directory_is_loose_only():
    string = '{"A/1.GIF", "A/2.GIF", "A/3.GIF"}'
    _fail(_SetPointer, string, test=1)
    _pass(_SetPointer, string, {"A/1.GIF", "A/2.GIF", "A/3.GIF"}, string, test=2)


def test_sequence_pointer_parses():
    string = '("1.GIF", "2.GIF", "3.GIF")'
    _pass(_SequencePointer, string, ["1.GIF", "2.GIF", "3.GIF"], string, list)


def test_sequence_pointer_directory_is_loose_only():
    string = '("A/1.GIF", "A/2.GIF", "A/3.GIF")'
    _fail(_SequencePointer, string, test=1)
    _pass(_SequencePointer, string, ["A/1.GIF", "A/2.GIF", "A/3.GIF"], string, test=2)


##########################################################################################
# _AttributeID and _PointerID
##########################################################################################

ID_TYPES = [(_AttributeID, ''), (_PointerID, '^')]


@pytest.mark.parametrize(('type_', 'prefix'), ID_TYPES)
@pytest.mark.parametrize('name', ['OBJECT', 'OBJECT_2', 'N123', 'N123:X456'])
def test_id_parses(type_, prefix, name):
    _pass(type_, prefix + name, prefix + name, prefix + name)


@pytest.mark.parametrize(('type_', 'prefix'), ID_TYPES)
@pytest.mark.parametrize('name', ['NAME_', 'NAME_:MORE', '_NAME', '1NAME', 'Name',
                                  'AAA:BBB:C'])
def test_id_rejects(type_, prefix, name):
    _fail(type_, prefix + name)


##########################################################################################
# _Statement and _EndStatement
##########################################################################################

@pytest.mark.parametrize(('string', 'value', 'strval'), [
    ('OBJECT\t   = COLUMN\n', ('OBJECT', 'COLUMN'), 'OBJECT = COLUMN'),
    ('OBJECT\t   = COLUMN\n   \n\t\r\t\n', ('OBJECT', 'COLUMN'), 'OBJECT = COLUMN'),
    ('^CASSINI:INDEX  = ("index.tab", 800 <bytes>)\n',
     ('^CASSINI:INDEX', ("index.tab", 800, '<BYTES>')),
     '^CASSINI:INDEX = ("index.tab", 800 <BYTES>)'),
])
def test_statement_parses(string, value, strval):
    _pass(_Statement, string, value, strval)


def test_statement_end_object_without_value_is_loose_only():
    _fail(_Statement, 'END_OBJECT\n', test=1)
    _pass(_Statement, 'END_OBJECT\n', ('END_OBJECT', None), 'END_OBJECT', test=2)


def test_end_statement():
    _pass(_EndStatement, 'END  \t\r\n', ('END', None), 'END')


##########################################################################################
