[![GitHub release; latest by date](https://img.shields.io/github/v/release/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/releases)
[![GitHub Release Date](https://img.shields.io/github/release-date/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/releases)
[![Test Status](https://img.shields.io/github/actions/workflow/status/SETI/rms-pdsparser/run-tests.yml?branch=main)](https://github.com/SETI/rms-pdsparser/actions)
[![Documentation Status](https://readthedocs.org/projects/rms-pdsparser/badge/?version=latest)](https://rms-pdsparser.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://img.shields.io/codecov/c/github/SETI/rms-pdsparser/main?logo=codecov)](https://codecov.io/gh/SETI/rms-pdsparser)
<br />
[![PyPI - Version](https://img.shields.io/pypi/v/rms-pdsparser)](https://pypi.org/project/rms-pdsparser)
[![PyPI - Format](https://img.shields.io/pypi/format/rms-pdsparser)](https://pypi.org/project/rms-pdsparser)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/rms-pdsparser)](https://pypi.org/project/rms-pdsparser)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rms-pdsparser)](https://pypi.org/project/rms-pdsparser)
<br />
[![GitHub commits since latest release](https://img.shields.io/github/commits-since/SETI/rms-pdsparser/latest)](https://github.com/SETI/rms-pdsparser/commits/main/)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/commits/main/)
[![GitHub last commit](https://img.shields.io/github/last-commit/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/commits/main/)
<br />
[![Number of GitHub open issues](https://img.shields.io/github/issues-raw/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/issues)
[![Number of GitHub closed issues](https://img.shields.io/github/issues-closed-raw/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/issues)
[![Number of GitHub open pull requests](https://img.shields.io/github/issues-pr-raw/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/pulls)
[![Number of GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/pulls)
<br />
![GitHub License](https://img.shields.io/github/license/SETI/rms-pdsparser)
[![Number of GitHub stars](https://img.shields.io/github/stars/SETI/rms-pdsparser)](https://github.com/SETI/rms-pdsparser/stargazers)
![GitHub forks](https://img.shields.io/github/forks/SETI/rms-pdsparser)

# Introduction

`pdsparser` is a Python module that reads a PDS3 label file and converts its entire
content to a Python dictionary.

It is supported by the PDS Ring-Moon Systems Node, SETI Institute.


# Installation

The `pdsparser` module is available via the `rms-pdsparser` package on PyPI and can be
installed with:

```sh
pip install rms-pdsparser
```

# Getting Started

The typical way to use this is as follows:

    from pdsparser import PdsLabel
    label = PdsLabel(label_path)

where `label_path` is the path to a PDS3 label file or a data file containing an attached
PDS3 label. The returned object `label` is an object of class
`PdsLabel`[![image](https://raw.githubusercontent.com/SETI/rms-pdsparser/main/icons/link.png)](https://rms-pdsparser.readthedocs.io/en/latest/module.html#__init__.PdsParser),
which supports the Python dictionary API and provides access to the content of the label.

# Example 1

Suppose this is the content of a PDS3 label:

    PDS_VERSION_ID                  = PDS3
    RECORD_TYPE                     = FIXED_LENGTH
    RECORD_BYTES                    = 2000
    FILE_RECORDS                    = 1001
    ^VICAR_HEADER                   = ("C3450702_GEOMED.IMG", 1)
    ^IMAGE                          = ("C3450702_GEOMED.IMG", 2000 <BYTES>)

    /* Image Description  */

    INSTRUMENT_HOST_NAME            = "VOYAGER 1"
    INSTRUMENT_HOST_NAME            = VG1
    IMAGE_TIME                      = 1980-10-29T09:58:10.00
    FILTER_NAME                     = VIOLET
    EXPOSURE_DURATION               = 1.920 <SECOND>

    DESCRIPTION                     = "This image is the result of geometrically
    correcting the corresponding CALIB image (C3450702_CALIB.IMG)."

    OBJECT                          = VICAR_HEADER
      HEADER_TYPE                   = VICAR
      BYTES                         = 2000
      RECORDS                       = 1
      INTERCHANGE_FORMAT            = ASCII
      DESCRIPTION                   = "VICAR format label for the image."
    END_OBJECT                      = VICAR_HEADER

    OBJECT                          = IMAGE
      LINES                         = 1000
      LINE_SAMPLES                  = 1000
      SAMPLE_TYPE                   = LSB_INTEGER
      SAMPLE_BITS                   = 16
      BIT_MASK                      = 16#7FFF#
    END_OBJECT                      = IMAGE
    END

This will be the returned dictionary:

    {'PDS_VERSION_ID': 'PDS3',
     'RECORD_TYPE': 'FIXED_LENGTH',
     'RECORD_BYTES': 2000,
     'FILE_RECORDS': 1001,
     '^VICAR_HEADER': 'C3450702_GEOMED.IMG',
     '^VICAR_HEADER_offset': 1,
     '^VICAR_HEADER_unit': '',
     '^VICAR_HEADER_fmt': '("C3450702_GEOMED.IMG", 1)',
     '^IMAGE': 'C3450702_GEOMED.IMG',
     '^IMAGE_offset': 2000,
     '^IMAGE_unit': '<BYTES>',
     '^IMAGE_fmt': '("C3450702_GEOMED.IMG", 2000 <BYTES>)',
     'INSTRUMENT_HOST_NAME_1': 'VOYAGER 1',
     'INSTRUMENT_HOST_NAME_2': 'VG1',
     'IMAGE_TIME': datetime.datetime(1980, 10, 29, 9, 58, 10),
     'IMAGE_TIME_day': -7003,
     'IMAGE_TIME_sec': 35890.0,
     'IMAGE_TIME_fmt': '1980-10-29T09:58:10.000',
     'FILTER_NAME': 'VIOLET',
     'EXPOSURE_DURATION': 1.92,
     'EXPOSURE_DURATION_unit': '<SECOND>',
     'DESCRIPTION': 'This image is the result of geometrically\n
    correcting the corresponding CALIB image (C3450702_CALIB.IMG).',
     'DESCRIPTION_unwrap': 'This image is the result of geometrically correcting the corresponding CALIB image (C3450702_CALIB.IMG).',
     'VICAR_HEADER': {'OBJECT': 'VICAR_HEADER',
                      'HEADER_TYPE': 'VICAR',
                      'BYTES': 2000,
                      'RECORDS': 1,
                      'INTERCHANGE_FORMAT': 'ASCII',
                      'DESCRIPTION': 'VICAR format label for the image.',
                      'END_OBJECT': 'VICAR_HEADER'},
     'IMAGE': {'OBJECT': 'IMAGE',
               'LINES': 1000,
               'LINE_SAMPLES': 1000,
               'SAMPLE_TYPE': 'LSB_INTEGER',
               'SAMPLE_BITS': 16,
               'BIT_MASK': 32767,
               'BIT_MASK_radix': 16,
               'BIT_MASK_digits': '7FFF',
               'BIT_MASK_fmt': '16#7FFF#',
               'END_OBJECT': 'IMAGE'},
     'END': '',
     'objects': ['VICAR_HEADER', 'IMAGE']}

As you can see:

* Most PDS3 label keywords become keys in the dictionary without change.
* OBJECTs and GROUPs are converted to sub-dictionaries and are keyed by the value of the
  PDS3 keyword. In this example, `label['VICAR_HEADER']['HEADER_TYPE']` returns "VICAR".
* If a keyword is repeated at the top level or within an object or group, it receives a
  suffix `_1`, `_2`, `_3`, etc. to distinguish it.
* If a value has units, there is an additional keyword in the dictionary with `_unit` as
  a suffix, containing the name of the unit.
* For text values that contain a newline, trailing blanks are suppressed. In addition, a
  dictionary key with the suffix `_unwrap` contains the same text as full paragraphs
  separated by newlines.
* For a file pointer of the form `(filename, offset)` or `(filename, offset <BYTES>)`, the
  keyed value is just the filename. The offset value provided with `_offset` appended to
  the dictionary key, and the unit is provided with `_unit` appended to the key.
* For based integers of the form `radix#digits#`, the dictionary value is converted to an
  integer. However, the radix and the digit string are provided using keys with the suffix
  `_radix` and `_digits`. Also, the key with suffix `_fmt` provides a full, PDS3-formatted
  version of the value.
* Dates and times are converted to Python datetime objects. However, additional dictionary
  keys appear with the suffix `_day` for the day number relative to Janary 1, 2000 and
  `_sec` for the elapsed seconds within that day.
* For items that have special formatting within a label, such file pointers, dates, and
  integers with a radix, the key with a `_fmt` suffix provides the PDS3-formatted value
  for reference.
* Each dictionary containing OBJECTs ends with an entry keyed by "objects", which returns
  the ordered list of all the OBJECT keys in that dictionary. Similarly, each dictionary
  containing GROUPs has an entry keyed by "groups", which returns the list of all the
  GROUP keys. These provide a easy way to iterate through objects and groups in the label.

# Example 2

Within `TABLE` and `SPREADSHEET` objects, the dictionary keys of the embedded `COLUMN`,
`BIT_COLUMN`, and `FIELD` objects are keyed by the value of the `NAME` keyword (rather than by
using repeated keywords `COLUMN_1`, `COLUMN_2`, `COLUMN_3`, etc.). For example, suppose
this appears in a PDS3 label:

    OBJECT = TABLE
      OBJECT = COLUMN
        NAME = VOLUME_ID
        START_BYTE = 1
      END_OBJECT = COLUMN
      OBJECT = COLUMN
        NAME = FILE_SPECIFICATION_NAME
        START_BYTE = 15
      END_OBJECT = COLUMN
    END_OBJECT = TABLE

The returned section of the dictionary will look like this:

    {'TABLE': {'OBJECT': 'TABLE',
                'VOLUME_ID': {'OBJECT': 'COLUMN',
                              'NAME': 'VOLUME_ID',
                              'START_BYTE': 1,
                              'END_OBJECT': 'COLUMN'},
                'FILE_SPECIFICATION_NAME': {'OBJECT': 'COLUMN',
                                            'NAME': 'FILE_SPECIFICATION_NAME',
                                            'START_BYTE': 15,
                                            'END_OBJECT': 'COLUMN'},
                'END_OBJECT': 'TABLE'},
    }

# Example 3

"Set" notation (using curly braces "{}") was sometimes mis-used in PDS3 labels where
"sequence" notation (using parentheses "()") was meant. For example, this might appear in
a label:

    CUTOUT_WINDOW = {1, 1, 200, 800}

which is supposed to define the four boundaries of an image region. The user might be
surprised to learn that in the dictionary, its value is the Python set `{1, 200, 800}`. To
address this situation, for every set value, the dictionary also has a key with the same
name but suffix `_list`, which contains the elements of the value as list in their
original order and including duplicates. In this example, the dictionary contains:

    'CUTOUT_WINDOW': {1, 200, 800},
    'CUTOUT_WINDOW_list': [1, 1, 200, 800]

# Options

The
`PdsLabel`[![image](https://raw.githubusercontent.com/SETI/rms-pdsparser/main/icons/link.png)](https://rms-pdsparser.readthedocs.io/en/latest/module.html#__init__.PdsParser.__init__),
constructor provides a variety of additional options for how to
parse the label and present its content.

* You can provide the label to be parsed as a string containing the label's content rather
  than as a path to a file.
* Use `types=True` to include the type of each keyword the file and interpret its content
  (e.g., "integer", "based_integer", "text", "date_time", or "file_offset_pointer") in the
  dictionary using the keyword plus suffix `_type`.
* Use `sources=True` to include the source text as extracted from the PDS3 label in the
  dictionary using the keyword plus suffix `_source`.
* Use `expand=True` to insert the content of any referenced `^STRUCTURE` keywords into the
  returned dictionary.
* Use `vax=True` to read attached labels from old-style Vax variable-length record files.
* Use the `repairs` option to correct any known syntax errors in the label prior to
  parsing using regular expressions.

Three methods of parsing the label are provided.

* `method="strict"` uses a strict implementation of the PDS3 syntax. It is sure to provide
  accurate results, but can be rather slow. This method can also be used to validate the
  syntax within a PDS3 label, because it will raise a SyntaxError if anything goes wrong.
* `method="loose"` uses a variant of the "strict" method, in which allowance is made for
  certain common syntax errors. Specifically,

  * It allows slashes in file names and in text strings that are not quoted (e.g., `N/A`).
  * It allows the value of `END_OBJECT` and `END_GROUP` to be absent, as long as they are
    still properly paired with associated `OBJECT` and `GROUP` keywords.
  * It allows time zone expressions (where were disallowed after the PDS2 standard).

* `method="fast"` is a different and much faster (often 30x faster) parser, which takes
  various "shortcuts" during the parsing. As a result, it may fail on occasions where the
  other methods succeed, and it may not return correct results in the cases of some
  oddly-formatted labels. However, it handles all the most common aspects of the PDS3
  syntax correctly, and so may be a good choice when handling large numbers of labels.

# Utilities

The `pdsparser` module provides several additional utilities for handling PDS3 labels.

- `read_label`[![image](https://raw.githubusercontent.com/SETI/rms-pdsparser/main/icons/link.png)](https://rms-pdsparser.readthedocs.io/en/latest/module.html#_utils.read_label):
  Reads a PDS3 label from a file. Supports attached labels
  within binary files.
- `read_vax_binary_label`[![image](https://raw.githubusercontent.com/SETI/rms-pdsparser/main/icons/link.png)](https://rms-pdsparser.readthedocs.io/en/latest/module.html#_utils.read_vax_binary_label):
  Reads the attached PDS3 label from an old-style
  Vax binary file that uses variable-length records.
- `expand_structures`[![image](https://raw.githubusercontent.com/SETI/rms-pdsparser/main/icons/link.png)](https://rms-pdsparser.readthedocs.io/en/latest/module.html#_utils.expand_structures):
  Replaces any `^STRUCTURE` keywords in a label string
  with the content of the associated ".FMT" files.

# Contributing

Information on contributing to this package can be found in the
[Contributing Guide](https://github.com/SETI/rms-pdsparser/blob/main/CONTRIBUTING.md).

# Links

- [Documentation](https://rms-pdsparser.readthedocs.io)
- [Repository](https://github.com/SETI/rms-pdsparser)
- [Issue tracker](https://github.com/SETI/rms-pdsparser/issues)
- [PyPi](https://pypi.org/project/rms-pdsparser)

# Licensing

This code is licensed under the [Apache License v2.0](https://github.com/SETI/rms-pdsparser/blob/main/LICENSE).
