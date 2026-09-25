##########################################################################################
# pdsparser/test_utils.py
##########################################################################################

import pathlib

import pytest

# Note: most functions in _utils.py are tested fully by test_labels.py.
import pdsparser
from pdsparser import is_pds3_file
from pdsparser._utils import _unwrap

ROOT_DIR = pathlib.Path(__file__).parent.parent
TEST_FILE_DIR = ROOT_DIR / 'test_files'


##########################################################################################
# is_pds3_file
##########################################################################################

@pytest.mark.parametrize('filepath', [
    # Detached labels
    TEST_FILE_DIR / 'v1877838443_1.lbl',
    str(TEST_FILE_DIR / 'JNCE_2022348_47C00007_V01.LBL'),
    # Attached labels starting with an SFDU label
    TEST_FILE_DIR / 'v1877838443_1.qub',
    TEST_FILE_DIR / 'C3438954.IMQ',             # Vax format
], ids=lambda path: pathlib.Path(path).name)
def test_is_pds3_file(filepath):
    assert is_pds3_file(filepath)


@pytest.mark.parametrize('filename', ['empty.dat', 'pdsdd-short.full', 'IRISHEDR.FMT'])
def test_is_not_pds3_file(filename):
    assert not is_pds3_file(TEST_FILE_DIR / filename)


def test_is_pds3_file_missing():
    with pytest.raises(FileNotFoundError):
        is_pds3_file(TEST_FILE_DIR / 'missing.lbl')


##########################################################################################
# Public API
##########################################################################################

@pytest.mark.parametrize('name', pdsparser.__all__)
def test_public_api(name):
    assert hasattr(pdsparser, name)


##########################################################################################
# _unwrap
##########################################################################################

UNWRAPPED_TABLE = ('Input data type.  Identify input type as follows:\n'
                   '\n'
                   ' 00000000 - Voyager 2;\n'
                   ' 00000001 - Voyager 1;\n'
                   ' 00000010 - Proof Test Model data;\n'
                   ' 00000011 - Not Used;\n'
                   ' 00000100 - External Simulation (DSN spacecraft 41);\n'
                   ' 00000101 - External Simulation (DSN spacecraft 42);\n'
                   ' 00000110 - Voyager 2 test data;\n'
                   ' 00000111 - Voyager 1 test data;\n'
                   ' 00001000 - Internal Simulation.')


def test_unwrap_paragraph():

    text = ('\n   \nThis image is the result of geometrically   \n'
            '    correcting the corresponding CALIB image (C3450702_CALIB.IMG).  \n'
            '\n')
    assert _unwrap(text) == ('This image is the result of geometrically '
                             'correcting the corresponding CALIB image '
                             '(C3450702_CALIB.IMG).')


def test_unwrap_explicit_newline_on_every_line():

    note = """Input data type.  Identify input type
        as follows:

         00000000 - Voyager 2;                               \\n
         00000001 - Voyager 1;                               \\n
         00000010 - Proof Test Model data;                   \\n
         00000011 - Not Used;                                \\n
         00000100 - External Simulation (DSN spacecraft 41); \\n
         00000101 - External Simulation (DSN spacecraft 42); \\n
         00000110 - Voyager 2 test data;                     \\n
         00000111 - Voyager 1 test data;                     \\n
         00001000 - Internal Simulation.                     """

    assert _unwrap(note) == UNWRAPPED_TABLE


def test_unwrap_indent_forces_newline():

    # Indented lines start a new line even without an explicit newline
    note = """Input data type.  Identify input type
        as follows:

         00000000 - Voyager 2;
         00000001 - Voyager 1;                               \\n
         00000010 - Proof Test Model data;
         00000011 - Not Used;                                \\n
         00000100 - External Simulation (DSN spacecraft 41);
         00000101 - External Simulation (DSN spacecraft 42); \\n
         00000110 - Voyager 2 test data;
         00000111 - Voyager 1 test data;                     \\n
         00001000 - Internal Simulation.                     """

    assert _unwrap(note) == UNWRAPPED_TABLE


def test_unwrap_without_blank_line():

    note = """Input data type.  Identify input type
        as follows:
         00000000 - Voyager 2;                               \\n
         00001000 - Internal Simulation.                     """

    assert _unwrap(note) == ('Input data type.  Identify input type as follows:\n'
                             ' 00000000 - Voyager 2;\n'
                             ' 00001000 - Internal Simulation.')


def test_unwrap_extra_blank_lines():

    # Multiple blank lines are reduced to one
    note = """Input data type.  Identify input type
        as follows:


         00000000 - Voyager 2;                               \\n
         00001000 - Internal Simulation.                     """

    assert _unwrap(note) == ('Input data type.  Identify input type as follows:\n'
                             '\n'
                             ' 00000000 - Voyager 2;\n'
                             ' 00001000 - Internal Simulation.')


def test_unwrap_paragraphs():

    desc = ('Telemetry format id from the minor frame of this line.\n'
            'Valid is 5-HIS, 6-HMA, 7-HCA, 17-HIM, 22-IM8, 23-AI8, and 25-IM4\n'
            '\n'
            'This is a second paragraph.\n'
            '\n'
            'This\n'
            'is\n'
            'a    \n'
            'third\n'
            'paragraph.\n'
            '\n'
            'This one has a\\nforced split.')

    assert _unwrap(desc) == ('Telemetry format id from the minor frame of this line. '
                             'Valid is 5-HIS, 6-HMA, 7-HCA, 17-HIM, 22-IM8, 23-AI8, and '
                             '25-IM4\n'
                             '\n'
                             'This is a second paragraph.\n'
                             '\n'
                             'This is a third paragraph.\n'
                             '\n'
                             'This one has a\n'
                             'forced split.')


##########################################################################################
