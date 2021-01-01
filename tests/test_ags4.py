# import sys
# Prepend path so that AGS4.py is loaded from project file
# instead of current installation
# sys.path.insert(0, './')
from python_ags4 import AGS4, __version__
import toml
import pandas as pd


def test_version():
    pyproject = toml.load('pyproject.toml')

    assert __version__ == pyproject['tool']['poetry']['version']


def test_AGS4_to_dict():
    tables, headings = AGS4.AGS4_to_dict('tests/test_data.ags')

    assert tables['PROJ']['PROJ_ID'][2] == '123456'


def test_AGS4_to_dataframe():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')

    assert tables['LOCA'].loc[2, 'LOCA_ID'] == 'Location_1'


def test_convert_to_numeric():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    LOCA = AGS4.convert_to_numeric(tables['LOCA'])

    assert LOCA.loc[0, 'LOCA_NATE'] == 100000.01
    assert LOCA.loc[2, 'LOCA_NATN'] == 5000000.20
    assert LOCA.loc[3, 'LOCA_FDEP'] == 50.44


def test_dataframe_to_AGS4():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')

    AGS4.dataframe_to_AGS4(tables, headings, 'tests/test.out')
    AGS4.dataframe_to_AGS4(tables, {}, 'tests/test.out')


def test_convert_to_text():
    tables, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
    LOCA_num = AGS4.convert_to_numeric(tables['LOCA'])
    LLPL_num = AGS4.convert_to_numeric(tables['LLPL'])

    LOCA_txt = AGS4.convert_to_text(LOCA_num, 'tests/DICT.ags')
    LLPL_txt = AGS4.convert_to_text(LLPL_num, 'tests/DICT.ags')

    # Decimal Points
    assert LOCA_txt.loc[0, 'LOCA_NATE'] == "100000.01"
    assert LOCA_txt.loc[2, 'LOCA_NATN'] == "5000000.20"
    assert LOCA_txt.loc[3, 'LOCA_FDEP'] == "50.44"

    # Siginificant Figgures
    assert LLPL_txt.loc[0, 'LLPL_LL'] == "55"
    assert LLPL_txt.loc[1, 'LLPL_PI'] == "130"

    # Should exit when called without a dictionary and without
    # UNIT & TYPE rows
    # AGS4.convert_to_text(LOCA_num)

    # Should return input entry without formatting if the data
    # is not numeric
    LLPL_txt = AGS4.convert_to_text(tables['LLPL'], 'tests/DICT.ags')
    assert LLPL_txt.loc[2, 'LLPL_LL'] == "55.1"
    assert LLPL_txt.loc[3, 'LLPL_PI'] == "134.8"


def test_AGS4_to_excel():
    AGS4.AGS4_to_excel('tests/test_data.ags', 'tests/test_data.xlsx')

    tables = pd.read_excel('tests/test_data.xlsx', sheet_name=None, engine='openpyxl')

    assert tables['PROJ'].loc[:, 'PROJ_ID'].values[2] == '123456'
    assert tables['LOCA'].loc[:, 'LOCA_ID'].values[1] == 'ID'
    assert tables['LOCA'].loc[:, 'LOCA_ID'].values[2] == 'Location_1'


def test_excel_to_AGS4():
    AGS4.excel_to_AGS4('tests/test.xlsx', 'tests/test.out')

    tables, _ = AGS4.AGS4_to_dataframe('tests/test.out')

    assert tables['LOCA'].loc[2, 'LOCA_NATN'] == '5000000.001'
    assert tables['LOCA'].loc[4, 'LOCA_NATN'] == '5000000.100'

    # Call function with dictionary file
    AGS4.excel_to_AGS4('tests/test.xlsx', 'tests/test.out', dictionary='tests/DICT.ags')

    tables, _ = AGS4.AGS4_to_dataframe('tests/test.out')

    assert tables['LOCA'].loc[2, 'LOCA_NATN'] == '5000000.00'
    assert tables['LOCA'].loc[4, 'LOCA_NATN'] == '5000000.10'
