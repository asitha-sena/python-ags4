

import toml
import pandas as pd
import pathlib
import pytest

from python_ags4 import AGS4, __version__

# Data in LOCA table in test_data.ags
LOCA = {'HEADING': ['UNIT', 'TYPE', 'DATA', 'DATA', 'DATA', 'DATA'],
        'LOCA_ID': ['', 'ID', 'Location_1', 'Location_2', 'Location_3', 'Location_4'],
        'LOCA_TYPE': ['', 'PA', 'Boring', 'Boring', 'Boring', 'Boring'],
        'LOCA_STAT': ['', 'PA', 'Draft', 'Draft', 'Draft', 'Draft'],
        'LOCA_NATE': ['m', '2DP', '100000.01', '101000.01', '102000.01', '103000.01'],
        'LOCA_NATN': ['m', '2DP', '5000000.20', '5000000.20', '5000000.20', '5000000.20'],
        'LOCA_GREF': ['', 'PA', '', '', '', ''],
        'LOCA_REM': ['', 'X', '', '', '', ''],
        'LOCA_FDEP': ['m', '2DP', '50.11', '50.22', '50.33', '50.44'],
        'LOCA_STAR': ['yyyy-mm-dd', 'DT', '2019-01-01', '2019-01-07', '2019-01-14', '2019-01-21'],
        'LOCA_PURP': ['',  'X', 'Geotechnical Investigation', 'Geotechnical Investigation', 'Geotechnical Investigation', 'Geotechnical Investigation'],
        'LOCA_TERM': ['', 'X', '', '', '', ''],
        'LOCA_ENDD': ['yyyy-mm-dd',  'DT', '2019-01-01', '2019-01-07', '2019-01-14', '2019-01-21']}

# Data in LLPL in test_data.ags
LLPL = {'HEADING': ['UNIT', 'TYPE', 'DATA', 'DATA'],
        'LOCA_ID': ['', 'ID', 'Location_1', 'Location_1'],
        'SAMP_TOP': ['m', '2DP', '1.00', '2.00'],
        'SAMP_REF': ['', 'X', '1a', '2a'],
        'SAMP_TYPE': ['', 'PA', 'Bag', 'Bag'],
        'SAMP_ID': ['', 'ID', '', ''],
        'SPEC_REF': ['', 'X', '', ''],
        'SPEC_DPTH': ['m', '2DP', '1.05', '2.05'],
        'LLPL_LL': ['%', '2SF', '55.1', '155.1'],
        'LLPL_PL': ['%', 'XN', '20.3', '20.3'],
        'LLPL_PI': ['', '2SF', '34.8', '134.8']}


def test_version():
    pyproject = toml.load('pyproject.toml')

    assert __version__ == pyproject['tool']['poetry']['version']


@pytest.mark.parametrize("test_file", ['tests/test_data.ags', pathlib.Path('tests/test_data.ags')])
def test_AGS4_file_to_dict(test_file, LOCA=LOCA):
    tables, headings = AGS4.AGS4_to_dict(test_file)

    assert tables['LOCA'] == LOCA


def test_AGS4_stream_to_dict(LOCA=LOCA):

    with open('tests/test_data.ags', 'r') as file:
        tables, headings = AGS4.AGS4_to_dict(file)

    assert tables['LOCA'] == LOCA


def test_AGS4_file_to_dataframe(LOCA=LOCA):
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')

    assert tables['LOCA'].loc[2, 'LOCA_ID'] == 'Location_1'
    assert tables['LOCA'].equals(pd.DataFrame(LOCA))


def test_AGS4_stream_to_dataframe(LOCA=LOCA):
    with open('tests/test_data.ags', 'r') as file:
        tables, headings = AGS4.AGS4_to_dataframe(file)

    assert tables['LOCA'].loc[2, 'LOCA_ID'] == 'Location_1'
    assert tables['LOCA'].equals(pd.DataFrame(LOCA))


def test_convert_to_numeric():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    LOCA = AGS4.convert_to_numeric(tables['LOCA'])

    assert LOCA.loc[0, 'LOCA_NATE'] == 100000.01
    assert LOCA.loc[2, 'LOCA_NATN'] == 5000000.20
    assert LOCA.loc[3, 'LOCA_FDEP'] == 50.44


def test_dataframe_to_AGS4():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')

    # Export with headings dictionary
    AGS4.dataframe_to_AGS4(tables, headings, 'tests/test.out')
    new_tables, new_headings = AGS4.AGS4_to_dataframe('tests/test.out')

    assert headings == new_headings
    assert tables['PROJ'].equals(new_tables['PROJ'])
    assert tables['TRAN'].equals(new_tables['TRAN'])
    assert tables['TYPE'].equals(new_tables['TYPE'])
    assert tables['UNIT'].equals(new_tables['UNIT'])
    assert tables['LOCA'].equals(new_tables['LOCA'])

    # Export without headings dictionary
    AGS4.dataframe_to_AGS4(tables, {}, 'tests/test.out')
    new_tables, new_headings = AGS4.AGS4_to_dataframe('tests/test.out')

    assert headings == new_headings
    assert tables['PROJ'].equals(new_tables['PROJ'])
    assert tables['TRAN'].equals(new_tables['TRAN'])
    assert tables['TYPE'].equals(new_tables['TYPE'])
    assert tables['UNIT'].equals(new_tables['UNIT'])
    assert tables['LOCA'].equals(new_tables['LOCA'])


def test_convert_to_text(LOCA=LOCA, LLPL=LLPL):
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    LOCA_num = AGS4.convert_to_numeric(tables['LOCA'])
    LLPL_num = AGS4.convert_to_numeric(tables['LLPL'])

    LOCA_txt = AGS4.convert_to_text(LOCA_num, 'tests/DICT.ags')
    LLPL_txt = AGS4.convert_to_text(LLPL_num, 'tests/DICT.ags')

    assert LOCA_txt.equals(pd.DataFrame(LOCA))

    # Siginificant Figgures
    assert LLPL_txt.loc[2, 'LLPL_LL'] == "55"
    assert LLPL_txt.loc[3, 'LLPL_PI'] == "130"

    # Should exit when called without a dictionary and without
    # UNIT & TYPE rows
    # AGS4.convert_to_text(LOCA_num)

    # Should return input entry without formatting if the data
    # is not numeric
    LLPL_txt = AGS4.convert_to_text(tables['LLPL'], 'tests/DICT.ags')

    assert LLPL_txt.equals(pd.DataFrame(LLPL))


def test_AGS4_to_excel(LOCA=LOCA, LLPL=LLPL):
    AGS4.AGS4_to_excel('tests/test_data.ags', 'tests/test_data.xlsx')

    tables = pd.read_excel('tests/test_data.xlsx', sheet_name=None, engine='openpyxl')

    assert tables['PROJ'].loc[:, 'PROJ_ID'].values[2] == '123456'
    assert tables['LOCA'].loc[:, 'LOCA_ID'].values[1] == 'ID'
    assert tables['LOCA'].loc[:, 'LOCA_ID'].values[2] == 'Location_1'


def test_AGS4_to_sorted_excel():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    AGS4.AGS4_to_excel('tests/test_data.ags', 'tests/test_data.xlsx', sort_tables=True)

    sorted_tables = pd.read_excel('tests/test_data.xlsx', sheet_name=None, engine='openpyxl')

    # dict keys first converted to lists to check order
    assert list(sorted(tables.keys())) == list(sorted_tables.keys())


def test_excel_to_AGS4():
    AGS4.excel_to_AGS4('tests/test.xlsx', 'tests/test.out')

    tables, _ = AGS4.AGS4_to_dataframe('tests/test.out')

    # Check whether numeric column have been formatted
    assert tables['LOCA'].loc[2, 'LOCA_NATN'] == '5000000.001'
    assert tables['LOCA'].loc[4, 'LOCA_NATN'] == '5000000.100'

    # Check whether stray data and columns have been dropped
    assert 'NEW_column' not in tables['LOCA'].columns
    assert 'NEWCOLUMN' not in tables['LOCA'].columns
    assert 'stray_data' not in tables['LOCA'].values

    # Call function with dictionary file
    AGS4.excel_to_AGS4('tests/test.xlsx', 'tests/test.out', dictionary='tests/DICT.ags')

    tables, _ = AGS4.AGS4_to_dataframe('tests/test.out')

    assert tables['LOCA'].loc[2, 'LOCA_NATN'] == '5000000.00'
    assert tables['LOCA'].loc[4, 'LOCA_NATN'] == '5000000.10'


def test_excel_to_AGS4_with_numeric_column_with_missing_TYPE():
    # Read LLPL table from xlsx file directly
    # LLPL_425 has numeric data but TYPE is erroneously set to ''
    LLPL = pd.read_excel('tests/test.xlsx', sheet_name='LLPL', engine='openpyxl')
    LLPL_425_from_xlsx = LLPL.loc[LLPL.HEADING.eq('DATA'), 'LLPL_425']\
                             .apply(pd.to_numeric, errors='coerce')\

    # Convert .xlsx file to AGS4 file and read it back
    AGS4.excel_to_AGS4('tests/test.xlsx', 'tests/test.out')
    tables, _ = AGS4.AGS4_to_dataframe('tests/test.out')
    LLPL_425_from_ags = tables['LLPL'].pipe(lambda df: df.loc[df.HEADING.eq('DATA'), 'LLPL_425'])\
                                      .apply(pd.to_numeric, errors='coerce')

    # Check whether LLPL_425 was exported even though TYPE is not specified
    assert LLPL_425_from_ags.equals(LLPL_425_from_xlsx)


def test_check_file():
    error_list = AGS4.check_file('tests/test_data.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')
    # assert error_list == ['Rule 1\t Line 12:\t Has one or more non-ASCII characters.',
    #                       'Rule 3\t Line 37:\t Consists only of spaces.',
    #                       'Rule 3\t Line 54:\t Does not start with a valid tag (i.e. GROUP, HEADING, TYPE, UNIT, or DATA).']

    # File without any errors
    error_list = AGS4.check_file('tests/test_files/example1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')
    assert 'Rule' not in error_list.keys()


@pytest.mark.parametrize("dict_version", ['4.1', '4.0.4', '4.0.3'])
def test_check_file_with_specified_dictionary_version(dict_version):
    error_list = AGS4.check_file('tests/test_data.ags', standard_AGS4_dictionary=dict_version)

    assert dict_version.replace('.', '_') in error_list['Metadata'][3]['desc']


@pytest.mark.parametrize("function", [AGS4.AGS4_to_dict, AGS4.AGS4_to_dataframe])
def test_duplicate_headers_with_rename_renames(function):
    tables, headers = function('tests/test_files/DuplicateHeaders.ags', rename_duplicate_headers=True)

    assert "SAMP_BASE_1" in headers['SAMP']


@pytest.mark.parametrize("function", [AGS4.AGS4_to_dict, AGS4.AGS4_to_dataframe, AGS4.check_file])
def test_duplicate_headers_without_rename_raises_error(function):
    with pytest.raises(AGS4.AGS4Error, match=r'HEADER row.*has duplicate entries'):
        function('tests/test_files/DuplicateHeaders.ags', rename_duplicate_headers=False)


def test_row_with_missing_field_raises_error():
    with pytest.raises(AGS4.AGS4Error, match=r'.*does not have the same number of entries as the HEADING row.*'):
        AGS4.AGS4_to_dict('tests/test_files/Row_with_missing_field.ags')


def test_converting_dataframe_without_UNIT_TYPE_to_text_raises_error():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    LOCA = AGS4.convert_to_numeric(tables['LOCA'])

    with pytest.raises(AGS4.AGS4Error, match=r'Cannot convert to text.*'):
        _ = AGS4.convert_to_text(LOCA)
