##########################################################################################
# pdsparser/test_labels.py
##########################################################################################

import datetime     # needed to eval the answer files
import pathlib

import pytest
from filecache import FCPath

from pdsparser import Pds3Label, PdsLabel, PdsError, PdsSyntaxError
from pdsparser._PDS3_GRAMMAR import _Text, _Integer

ROOT_DIR = pathlib.Path(__file__).parent.parent
TEST_FILE_DIR = ROOT_DIR / 'test_files'

# Quote the unquoted N/A values in v1877838443_1.lbl, so method='strict' can parse it
N_A_REPAIR = (r'(?<!["\'])N/A', "'N/A'")


def _answer(filename):
    """The dictionary stored in an answer file."""
    return eval((TEST_FILE_DIR / filename).read_text())


def _quote_n_a_sources(answer):
    """Update an answer dictionary for the effect of N_A_REPAIR."""
    for key in ('GAIN_MODE_ID_source', 'BACKGROUND_SAMPLING_MODE_ID_source'):
        answer[key] = answer[key].replace('N/A', "'N/A'")
    return answer


##########################################################################################
# COVIMS_0xxx: v1877838443_1
##########################################################################################

COVIMS_LBL = TEST_FILE_DIR / 'v1877838443_1.lbl'


# This file has an un-quoted N/A, so method='loose'
@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_covims(method):
    label = Pds3Label(COVIMS_LBL, method=method, types=True, sources=True, expand=False)
    assert label.dict == _answer('v1877838443_1-lbl-answer.txt')


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_covims_repaired(method):
    label = Pds3Label(COVIMS_LBL, method=method, types=True, sources=True, expand=False,
                      repairs=N_A_REPAIR)
    assert label.dict == _quote_n_a_sources(_answer('v1877838443_1-lbl-answer.txt'))


def test_covims_first_suffix_false():

    label = Pds3Label(COVIMS_LBL, method='strict', types=True, sources=True,
                      expand=False, repairs=N_A_REPAIR, first_suffix=False)

    answer = _quote_n_a_sources(_answer('v1877838443_1-lbl-answer.txt'))
    subdict = answer['SPECTRAL_QUBE']
    for key in ('^STRUCTURE_1', '^STRUCTURE_1_type', '^STRUCTURE_1_source',
                '^STRUCTURE_1_fmt'):
        subdict[key[:10] + key[12:]] = subdict.pop(key)

    assert label.dict == answer


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_covims_expanded(method):
    label = Pds3Label(COVIMS_LBL, method=method, types=True, sources=True, expand=True)
    assert label.dict == _answer('v1877838443_1-lbl-expanded.txt')


def test_covims_expanded_unused_fmt_dirs():

    # The .FMT file is found next to the label, so this value of fmt_dirs is not used
    label = Pds3Label(COVIMS_LBL, method='loose', types=True, sources=True, expand=True,
                      fmt_dirs=['./'])
    assert label.dict == _answer('v1877838443_1-lbl-expanded.txt')


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_covims_expanded_repaired(method):
    label = Pds3Label(COVIMS_LBL, method=method, types=True, sources=True, expand=True,
                      repairs=N_A_REPAIR)
    assert label.dict == _quote_n_a_sources(_answer('v1877838443_1-lbl-expanded.txt'))


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_covims_attached_label(method):
    label = Pds3Label(TEST_FILE_DIR / 'v1877838443_1.qub', method=method, types=True,
                      sources=True)
    assert label.dict == _answer('v1877838443_1-qub-answer.txt')


@pytest.mark.parametrize(('filename', 'message'), [
    ('v1877838443_1-EXCEPTION.lbl', r'Expected end of text, found .*'),
    ('v1877838443_1-EXCEPTION2.lbl', 'missing END_OBJECT'),
    ('v1877838443_1-EXCEPTION3.lbl', 'unbalanced END_OBJECT'),
])
def test_covims_syntax_errors(filename, message):
    with pytest.raises(PdsSyntaxError, match=message):
        Pds3Label(TEST_FILE_DIR / filename, method='loose')


##########################################################################################
# GOxxx_v1: C052079-2800R
##########################################################################################

GO_LBL = TEST_FILE_DIR / 'C052079-2800R.LBL'


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_go(method):
    label = Pds3Label(GO_LBL, method=method, types=True, sources=True, expand=False)
    assert label.dict == _answer('C052079-2800R-answer.txt')


def test_go_vax_ignored_for_label_file():
    label = Pds3Label(GO_LBL, method='loose', types=True, sources=True, expand=False,
                      vax=True)
    assert label.dict == _answer('C052079-2800R-answer.txt')


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_go_expanded(method):
    label = Pds3Label(GO_LBL, method=method, types=True, sources=True, expand=True)
    assert label.dict == _answer('C052079-2800R-expanded.txt')


##########################################################################################
# JNOJIR_xxxx, JNOJNC_0xxx, NHxxLO_xxxx
##########################################################################################

# This answer file predates first_suffix=True as the default
@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_jnojir(method):
    label = Pds3Label(TEST_FILE_DIR / 'JIR_LOG_SPE_RDR_2020048T195001_V01.LBL',
                      method=method, types=True, sources=True, first_suffix=False)
    assert label.dict == _answer('JIR_LOG_SPE_RDR_2020048T195001_V01-answer.txt')


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_jnojnc(method):
    label = Pds3Label(TEST_FILE_DIR / 'JNCE_2022348_47C00007_V01.LBL', method=method,
                      types=True, sources=True)
    assert label.dict == _answer('JNCE_2022348_47C00007_V01-answer.txt')


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_nhxxlo(method):
    label = Pds3Label(TEST_FILE_DIR / 'lor_0284676508_0x630_sci.lbl', method=method,
                      types=True, sources=True)
    assert label.dict == _answer('lor_0284676508_0x630_sci-answer.txt')


##########################################################################################
# VGISS_xxxx: C3450702_GEOMED
##########################################################################################

VGISS_LBL = TEST_FILE_DIR / 'C3450702_GEOMED.LBL'


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_vgiss(method):
    label = Pds3Label(VGISS_LBL, method=method, types=True, sources=True)
    assert label.dict == _answer('C3450702_GEOMED-answer.txt')


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_vgiss_without_types_or_sources(method):
    label = Pds3Label(VGISS_LBL, method=method)
    assert label.dict == _answer('C3450702_GEOMED-short.txt')


def test_dict_api():

    label = Pds3Label(VGISS_LBL, method='strict')
    assert len(label) == 61

    pairs = [('PDS_VERSION_ID', 'PDS3'),
             ('RECORD_TYPE', 'FIXED_LENGTH'),
             ('RECORD_BYTES', 2000),
             ('FILE_RECORDS', 1001),
             ('^VICAR_HEADER', 'C3450702_GEOMED.IMG'),
             ('^VICAR_HEADER_offset', 1),
             ('^VICAR_HEADER_unit', ''),
             ('^VICAR_HEADER_fmt', '("C3450702_GEOMED.IMG", 1)'),
             ('^IMAGE', 'C3450702_GEOMED.IMG'),
             ('^IMAGE_offset', 2),
             ('^IMAGE_unit', ''),
             ('^IMAGE_fmt', '("C3450702_GEOMED.IMG", 2)'),
             ('DATA_SET_ID', 'VG1/VG2-S-ISS-2/3/4/6-PROCESSED-V1.1'),
             ('PRODUCT_ID', 'C3450702_GEOMED.IMG'),
             ('PRODUCT_CREATION_TIME', datetime.datetime(2012, 5, 1, 16, 0)),
             ('PRODUCT_CREATION_TIME_day', 4504),
             ('PRODUCT_CREATION_TIME_sec', 57600),
             ('PRODUCT_CREATION_TIME_fmt', '2012-05-01T16:00:00')]
    assert list(label.items())[:18] == pairs
    assert list(label.keys())[:18] == [p[0] for p in pairs]
    assert list(label.values())[:18] == [p[1] for p in pairs]

    assert label['PDS_VERSION_ID'] == 'PDS3'
    assert label.get('PDS_VERSION_ID', 'whatever') == 'PDS3'
    assert label.get('PDS_VERSION_IDx', 'whatever') == 'whatever'
    assert 'PDS_VERSION_ID' in label
    assert 'PDS_VERSION_IDx' not in label


@pytest.mark.parametrize('method', ['strict', 'fast'])
@pytest.mark.parametrize('func', [str, repr])
def test_str_and_repr(method, func):

    label = Pds3Label(VGISS_LBL, method=method)
    lines = func(label).split('\n')
    assert lines[:9] == ['PDS_VERSION_ID = PDS3',
                         'RECORD_TYPE = FIXED_LENGTH',
                         'RECORD_BYTES = 2000',
                         'FILE_RECORDS = 1001',
                         '^VICAR_HEADER = ("C3450702_GEOMED.IMG", 1)',
                         '^IMAGE = ("C3450702_GEOMED.IMG", 2)',
                         'DATA_SET_ID = "VG1/VG2-S-ISS-2/3/4/6-PROCESSED-V1.1"',
                         'PRODUCT_ID = "C3450702_GEOMED.IMG"',
                         'PRODUCT_CREATION_TIME = 2012-05-01T16:00:00']


def test_deprecated_constructors():

    label = Pds3Label(VGISS_LBL, method='strict')

    assert Pds3Label.from_file(str(VGISS_LBL)).dict == label.dict
    assert Pds3Label.from_string(label.content).dict == label.dict

    lines = Pds3Label.load_file(FCPath(VGISS_LBL))
    assert ''.join(lines) == label.content
    assert Pds3Label.from_string(lines).dict == label.dict


def test_details():

    label = Pds3Label(VGISS_LBL, method='strict', _details=True)

    detail = label['^VICAR_HEADER_detail']
    assert detail.value == label['^VICAR_HEADER']
    assert detail.offset == 1
    assert detail.unit == ''
    assert detail.source == '("C3450702_GEOMED.IMG", 1)'
    assert str(detail) == '("C3450702_GEOMED.IMG", 1)'

    detail = label['EXPOSURE_DURATION_detail']
    assert detail.value == 1.92
    assert detail.unit == '<SECOND>'
    assert str(detail) == '1.92 <SECOND>'

    detail = label['FILTER_NAME_detail']
    assert detail.value == 'VIOLET'
    assert str(detail) == 'VIOLET'


@pytest.mark.parametrize('vax', [False, True])
def test_detached_label_fallback(vax):

    # This data file contains no label, so the detached label is read instead
    label = Pds3Label(TEST_FILE_DIR / 'C3450702_GEOMED.empty', method='strict',
                      types=True, sources=True, vax=vax)
    assert label.dict == _answer('C3450702_GEOMED-answer.txt')


##########################################################################################
# VG_0xxx: C3438954
##########################################################################################

VG_IMQ = TEST_FILE_DIR / 'C3438954.IMQ'


def _remove_sources(answer):
    """Remove the "_source" keys from the C3438954 answer dictionary."""

    for obj in ('IMAGE_HISTOGRAM', 'ENCODING_HISTOGRAM', 'ENGINEERING_TABLE', 'IMAGE'):
        for key in list(answer[obj]):
            if key.endswith('_source'):
                del answer[obj][key]
    for key in list(answer):
        if key.endswith('_source'):
            del answer[key]
    return answer


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_vg_vax(method):
    label = Pds3Label(VG_IMQ, method=method, types=True, sources=True, expand=False,
                      vax=True)
    assert label.dict == _answer('C3438954-answer.txt')


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_vg_vax_without_sources(method):
    label = Pds3Label(VG_IMQ, method=method, types=True, sources=False, expand=False,
                      vax=True)
    assert label.dict == _remove_sources(_answer('C3438954-answer.txt'))


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_vg_vax_expanded(method):
    label = Pds3Label(VG_IMQ, method=method, types=True, sources=True, expand=True,
                      vax=True, first_suffix=False)
    assert label.dict == _answer('C3438954-expanded.txt')


##########################################################################################
# VG_2001: VG2_SAT
##########################################################################################

VG2_LBL = TEST_FILE_DIR / 'VG2_SAT.LBL'
VG2_FMT_REPAIR = (r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR.FMT"')
VG2_BAD_FMT_REPAIRS = [(r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR-with-error.FMT"'),
                       (r'data identifier\.', 'data identifier."')]


@pytest.mark.parametrize('method', ['strict', 'fast'])
def test_vg2_sat(method):
    label = Pds3Label(VG2_LBL, method=method, types=True, sources=True, expand=False)
    assert label.dict == _answer('VG2_SAT-answer.txt')


def test_vg2_sat_structure_file_not_found():

    # The name of the ^STRUCTURE file is erroneous
    with pytest.raises(FileNotFoundError):
        Pds3Label(VG2_LBL, method='strict', expand=True)


# method='loose' because the FMT file has tabs
@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_vg2_sat_expanded(method):
    label = Pds3Label(VG2_LBL, method=method, types=False, sources=True, expand=True,
                      repairs=VG2_FMT_REPAIR)
    assert label.dict == _answer('VG2_SAT-expanded.txt')


def test_vg2_sat_structure_syntax_error():

    # This FMT has a missing quote in the first DESCRIPTION
    with pytest.raises(PdsSyntaxError, match=r'Expected end of text, found .*'):
        Pds3Label(VG2_LBL, method='loose', expand=True, repairs=VG2_BAD_FMT_REPAIRS[:1])


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_vg2_sat_structure_repaired(method):

    # Repairs are also applied to the content of the .FMT file
    label = Pds3Label(VG2_LBL, method=method, types=False, sources=True, expand=True,
                      repairs=VG2_BAD_FMT_REPAIRS)
    assert label.dict == _answer('VG2_SAT-expanded.txt')


def test_expand_without_label_path():

    # Without a label path or fmt_dirs, the local default directory is searched; the
    # .FMT file is not there
    with pytest.raises(FileNotFoundError):
        Pds3Label(VG2_LBL.read_text(), expand=True)


##########################################################################################
# PDS data dictionary
##########################################################################################

def test_compound():
    label = Pds3Label(TEST_FILE_DIR / 'pdsdd-short.full', method='compound')
    assert label.dict == _answer('pdsdd-short-answer.txt')


def test_compound_without_end_statements():

    compound = Pds3Label(TEST_FILE_DIR / 'pdsdd-short.full', method='compound')
    expected = {key: value for key, value in compound.dict.items()
                if not key.startswith('END_')}
    expected['END'] = compound['END_21']

    # method='loose' because of missing commas in sequences
    label = Pds3Label(TEST_FILE_DIR / 'pdsdd-endless.full', method='loose')
    assert label.dict == expected


##########################################################################################
# TESTS.LBL
##########################################################################################

TESTS_LBL = TEST_FILE_DIR / 'TESTS.LBL'


def test_tests_label_loose():
    label = Pds3Label(TESTS_LBL, method='loose', types=True, sources=True)
    assert label.dict == _answer('TESTS-answer.txt')


def test_tests_label_fast():

    answer = _answer('TESTS-answer.txt')
    answer['MIXED_SEQ_unit'] = '<km>'

    label = Pds3Label(TESTS_LBL, method='fast', types=True, sources=True)
    assert label.dict == answer


##########################################################################################
# Label inputs and the filepath attribute
##########################################################################################

QUB_FILE = TEST_FILE_DIR / 'v1877838443_1.qub'


@pytest.fixture
def qub_content():
    return Pds3Label(QUB_FILE, method='strict').content


def test_label_from_content_string(qub_content):
    label = PdsLabel(qub_content, method='strict', types=True, sources=True)
    assert label.dict == _answer('v1877838443_1-qub-answer.txt')


def test_label_from_list_of_strings(qub_content):
    label = PdsLabel(qub_content.split('\n'), method='strict', types=True, sources=True)
    assert label.dict == _answer('v1877838443_1-qub-answer.txt')


@pytest.mark.parametrize('path', [QUB_FILE, str(QUB_FILE), FCPath(QUB_FILE)])
def test_filepath(path):

    label = Pds3Label(path)
    assert isinstance(label.filepath, FCPath)
    assert label.filepath == FCPath(QUB_FILE)
    assert label._filepath == label.filepath        # deprecated name


def test_filepath_is_none_for_content(qub_content):

    for label in (Pds3Label(qub_content), Pds3Label(qub_content.split('\n'))):
        assert label.filepath is None
        assert label._filepath is None


def test_invalid_method():
    with pytest.raises(ValueError, match='invalid method'):
        PdsLabel(QUB_FILE, method='whatever')


def test_invalid_label():
    with pytest.raises(ValueError, match='invalid label'):
        PdsLabel(999)


def test_setitem(qub_content):

    label = Pds3Label(qub_content)
    label['FOO'] = 'BAR'
    assert label.dict['FOO'] == 'BAR'


##########################################################################################
# Syntax errors
##########################################################################################

@pytest.mark.parametrize('vax', [False, True])
def test_missing_end_statement(vax):
    with pytest.raises(PdsSyntaxError, match=r'missing END statement in .*empty\.dat'):
        Pds3Label(TEST_FILE_DIR / 'empty.dat', vax=vax)


def test_syntax_error_classes():

    assert issubclass(PdsSyntaxError, SyntaxError)
    assert issubclass(PdsSyntaxError, PdsError)

    with pytest.raises(SyntaxError):
        Pds3Label(TEST_FILE_DIR / 'empty.dat')
    with pytest.raises(PdsError):
        Pds3Label(TEST_FILE_DIR / 'empty.dat')


def test_mixed_units_fast():

    content = 'VECTOR = (1 <km>, 10 <s>)\nEND\n'
    Pds3Label(content)          # no problem if method='strict'
    with pytest.raises(PdsSyntaxError,
                       match=r'mixture of units encountered at VECTOR, .*'):
        Pds3Label(content, method='fast')


@pytest.mark.parametrize('method', ['strict', 'loose', 'fast'])
@pytest.mark.parametrize(('content', 'message'), [
    ('OBJECT = FOO\nEND\n', r'missing END_OBJECT.*'),
    ('OBJECT = FOO\nEND_OBJECT = BAR\nEND\n', r'unbalanced END_OBJECT = BAR.*'),
    ('END_OBJECT = BAR\nEND\n', r'unbalanced END_OBJECT = BAR.*'),
    ('VALUE = "abc\nEND\n', r'Expected \'"\', found end of text.*'),
])
def test_syntax_error(method, content, message):
    with pytest.raises(PdsSyntaxError, match=message):
        Pds3Label(content, method=method)


def test_end_object_without_value_strict():
    with pytest.raises(PdsSyntaxError, match=r"found '\\n' .*"):
        Pds3Label('END_OBJECT\nEND\n', method='strict')


@pytest.mark.parametrize('method', ['loose', 'fast'])
def test_end_object_without_value_unbalanced(method):
    with pytest.raises(PdsSyntaxError, match=r'unbalanced END_OBJECT[^=]*'):
        Pds3Label('END_OBJECT\nEND\n', method=method)


@pytest.mark.parametrize(('content', 'message'), [
    ('VALUE = (1,2\nEND\n', r'unbalanced parentheses \(\)'),
    ('VALUE = {1,2\nEND\n', 'unbalanced braces {}'),
    ('VALUE\nEND\n', 'missing "=" at VALUE, line 1'),
])
def test_syntax_error_fast(content, message):
    with pytest.raises(PdsSyntaxError, match=message):
        Pds3Label(content, method='fast')


##########################################################################################
# Special cases of label content
##########################################################################################

def test_details_from_content():

    content = 'OBJECT = TEST\nVALUE = 7\nEND_OBJECT\nEND\n'
    label = Pds3Label(content, method='loose', _details=True)
    assert label.dict == {'TEST': {'OBJECT': 'TEST',
                                   'OBJECT_detail': _Text('', 0, ['TEST']),
                                   'VALUE': 7,
                                   'VALUE_detail': _Integer('', 0, ['7']),
                                   'END_OBJECT': 'TEST'},
                          'END': None,
                          'objects': ['TEST']}


@pytest.mark.parametrize('content', ['VALUE = 7\nEND', 'VALUE = 7\nEND    \t  '])
def test_end_without_terminator(content):
    label = Pds3Label(content, method='loose')
    assert label.dict == {'VALUE': 7, 'END': None}


@pytest.mark.parametrize(('content', 'expected'), [
    ('VALUE = (1, 2, 3 4)\n', {'VALUE': [1, 2, 3, 4]}),
    ('VALUE = {1, 2, 3 4 1}\n', {'VALUE': {1, 2, 3, 4}, 'VALUE_list': [1, 2, 3, 4, 1]}),
    ('VALUE = ((1, 2) (3\n "four"))\n', {'VALUE': [[1, 2], [3, "four"]]}),
])
def test_missing_commas(content, expected):
    label = Pds3Label(content, method='loose')
    assert label.dict == expected


##########################################################################################
# Dates and times with blanks where zeros belong
##########################################################################################

BLANK_DATES = ['2001- 2- 3', '2004-05- 6', '2007- 8-09', '2010-  3', '2014- 56']
BLANK_HOURS = [' 6', '07']
BLANK_MINUTES = ['08', ' 9']
BLANK_SECONDS = [' 1', '02', ' 5.678']
BLANK_ZONES = ['-2', '+ 3', '-4: 0', '+05: 0']
BLANK_ZONED_TIMES = [' 2:34:56', ' 2: 3: 4', '12:34: 5.67']

methods = pytest.mark.parametrize('method', ['fast', 'loose'])
quotes = pytest.mark.parametrize('quote', ['', '"'], ids=['unquoted', 'quoted'])


def _assert_same_label(name, value1, value2, quote, method):
    """Parse NAME = value1 and NAME = value2 and confirm the dicts are equal.

    Returns the first label's dictionary.
    """

    d1 = Pds3Label(f'{name} = {quote}{value1}{quote}\n', method=method).dict
    d2 = Pds3Label(f'{name} = {quote}{value2}{quote}\n', method=method).dict
    assert d1 == d2
    return d1


def _hm(hh, mm):
    """Time strings HH:MM with and without blanks for zeros."""

    time1 = f'{hh}:{mm}'
    time2 = time1.replace(' ', '0')
    return time1, time2


@methods
@quotes
@pytest.mark.parametrize('date', BLANK_DATES)
def test_blank_date(method, quote, date):
    fixed = date.replace(' ', '0')
    d1 = _assert_same_label('DATE', date, fixed, quote, method)
    assert d1['DATE_fmt'] == fixed


@methods
@quotes
@pytest.mark.parametrize('hh', BLANK_HOURS)
@pytest.mark.parametrize('mm', BLANK_MINUTES)
def test_blank_hm_time(method, quote, hh, mm):
    time1, time2 = _hm(hh, mm)
    d1 = _assert_same_label('TIME', time1, time2, quote, method)
    assert d1['TIME_fmt'] == time2 + ':00'


@methods
@quotes
@pytest.mark.parametrize('hh', BLANK_HOURS)
@pytest.mark.parametrize('mm', BLANK_MINUTES)
@pytest.mark.parametrize('ss', BLANK_SECONDS)
def test_blank_hms_time(method, quote, hh, mm, ss):
    time1, time2 = _hm(hh, mm)
    time1, time2 = f'{time1}:{ss}', f'{time2}:{ss.replace(" ", "0")}'
    d1 = _assert_same_label('TIME', time1, time2, quote, method)
    assert d1['TIME_fmt'] == time2


@methods
@quotes
@pytest.mark.parametrize('date', BLANK_DATES)
@pytest.mark.parametrize('hh', BLANK_HOURS)
@pytest.mark.parametrize('mm', BLANK_MINUTES)
def test_blank_hm_date_time(method, quote, date, hh, mm):
    time1, time2 = _hm(hh, mm)
    dt1 = f'{date}T{time1}'
    dt2 = f'{date.replace(" ", "0")}T{time2}'
    d1 = _assert_same_label('DATE', dt1, dt2, quote, method)
    assert d1['DATE_fmt'] == dt2 + ':00'


@methods
@quotes
@pytest.mark.parametrize('date', BLANK_DATES)
@pytest.mark.parametrize('hh', BLANK_HOURS)
@pytest.mark.parametrize('mm', BLANK_MINUTES)
@pytest.mark.parametrize('ss', BLANK_SECONDS)
def test_blank_hms_date_time(method, quote, date, hh, mm, ss):
    time1, time2 = _hm(hh, mm)
    dt1 = f'{date}T{time1}:{ss}'
    dt2 = f'{date.replace(" ", "0")}T{time2}:{ss.replace(" ", "0")}'
    d1 = _assert_same_label('DATE', dt1, dt2, quote, method)
    assert d1['DATE_fmt'] == dt2


# Time zones are only supported by method='loose'
@quotes
@pytest.mark.parametrize('zone', BLANK_ZONES)
@pytest.mark.parametrize('hms', BLANK_ZONED_TIMES)
def test_blank_zoned_time(quote, zone, hms):

    time1 = hms + zone
    time2 = time1.replace(' ', '0')
    _assert_same_label('TIME', time1, time2, quote, 'loose')
    _assert_same_label('DATE', '2012-01-23T' + time1, '2012-01-23T' + time2, quote,
                       'loose')


##########################################################################################
# as_dict
##########################################################################################

def test_as_dict():

    test_dict = Pds3Label(TEST_FILE_DIR / 'AS_DICT_TEST.LBL').as_dict()

    # This is the result of a run of the v1 module...
    old_answer = _answer('AS_DICT_TEST-as_dict.txt')

    # new parser does not use "Z" suffix
    test_dict['IMAGE_TIME'] = test_dict['IMAGE_TIME'] + 'Z'

    # a line break in an embedded string is now just a space
    product_ids = test_dict['SOURCE_PRODUCT_ID']
    product_ids[4] = product_ids[4].replace(' ', '\n')

    # old dicts do not have OBJECT and END_OBJECT entries
    for key in ('IMAGE_HEADER', 'TELEMETRY_TABLE', 'BAD_DATA_VALUES_HEADER', 'IMAGE'):
        del test_dict[key]['OBJECT']
        del test_dict[key]['END_OBJECT']

    # old dicts do not contain END statement
    del test_dict['END']

    assert test_dict == old_answer


##########################################################################################
