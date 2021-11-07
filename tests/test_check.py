
import os

from python_ags4 import AGS4, __version__

def test_rule_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 2' in error_list.keys()
    assert error_list['AGS Format Rule 2'][0]['line'] == 60
    assert error_list['AGS Format Rule 2'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 2'][0]['desc'] == 'No DATA rows in group.'

    assert 'Metadata' in error_list.keys()
    assert error_list['Metadata'][0]['desc'] == '4.1-rule2.ags'
    assert error_list['Metadata'][2]['desc'] == f'python_ags4 v{__version__}'
    assert error_list['Metadata'][3]['desc'] == 'Standard_dictionary_v4_1.ags'


def test_rule_2b_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b1.ags')

    assert 'AGS Format Rule 2b' in error_list.keys()
    assert error_list['AGS Format Rule 2b'][0]['line'] == 7
    assert error_list['AGS Format Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][0]['desc'] == 'UNIT row missing from group.'

    assert 'Metadata' in error_list.keys()
    assert error_list['Metadata'][0]['desc'] == '4.1-rule2b1.ags'
    assert error_list['Metadata'][2]['desc'] == f'python_ags4 v{__version__}'
    assert error_list['Metadata'][3]['desc'] == 'Standard_dictionary_v4_1.ags'


def test_rule_2b_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 2b' in error_list.keys()
    assert error_list['AGS Format Rule 2b'][0]['line'] == 7
    assert error_list['AGS Format Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][0]['desc'] == 'UNIT row missing from group.'

    assert error_list['AGS Format Rule 2b'][1]['line'] == 7
    assert error_list['AGS Format Rule 2b'][1]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][1]['desc'] == 'TYPE row missing from group.'


def test_rule_2b_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 2b' in error_list.keys()
    assert error_list['AGS Format Rule 2b'][0]['line'] == 7
    assert error_list['AGS Format Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][0]['desc'] == 'TYPE row missing from group.'


def test_rule_2b_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 2b' in error_list.keys()
    assert error_list['AGS Format Rule 2b'][0]['line'] == 10
    assert error_list['AGS Format Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][0]['desc'] == 'UNIT row is misplaced. It should be immediately below the HEADING row.'

    assert error_list['AGS Format Rule 2b'][1]['line'] == 9
    assert error_list['AGS Format Rule 2b'][1]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 2b'][1]['desc'] == 'TYPE row is misplaced. It should be immediately below the UNIT row.'


def test_rule_2c():
    error_list = AGS4.check_file('tests/test_files/DuplicateHeaders.ags')

    assert 'AGS Format Rule 2c' in error_list.keys()
    assert error_list['AGS Format Rule 2c'][0]['line'] == 81
    assert error_list['AGS Format Rule 2c'][0]['desc'] == 'HEADER row has duplicate fields.'


def test_rule_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 3' in error_list.keys()
    assert error_list['AGS Format Rule 3'][0]['line'] == 58
    assert error_list['AGS Format Rule 3'][0]['desc'] == 'Does not start with a valid data descriptor.'


def test_rule_7():
    error_list = AGS4.check_file('tests/test_files/4.1-rule7-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 7' in error_list.keys()
    assert error_list['AGS Format Rule 7'][0]['line'] == 2
    assert error_list['AGS Format Rule 7'][0]['group'] == 'PROJ'
    assert error_list['AGS Format Rule 7'][0]['desc'] == 'Headings not in order starting from FILE_FSET. Expected order: ...PROJ_MEMO|FILE_FSET'


def test_rule_8_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][0]['line'] == 76
    assert error_list['AGS Format Rule 8'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][0]['desc'] == 'Value 523145.010 in LOCA_NATE not of data type 2DP.'

    assert error_list['AGS Format Rule 8'][1]['line'] == 77
    assert error_list['AGS Format Rule 8'][1]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][1]['desc'] == 'Value 523145.0 in LOCA_NATE not of data type 2DP.'


def test_rule_8_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][0]['line'] == 82
    assert error_list['AGS Format Rule 8'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][0]['desc'] == 'Value 2.455e1 in SAMP_TOP not of data type 2SCI.'

    assert error_list['AGS Format Rule 8'][1]['line'] == 83
    assert error_list['AGS Format Rule 8'][1]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][1]['desc'] == 'Value 30.45e1 in SAMP_TOP not of data type 2SCI.'

    assert error_list['AGS Format Rule 8'][2]['line'] == 84
    assert error_list['AGS Format Rule 8'][2]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][2]['desc'] == 'Value 3.4e1 in SAMP_TOP not of data type 2SCI.'


def test_rule_8_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][0]['line'] == 70
    assert error_list['AGS Format Rule 8'][0]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 8'][0]['desc'] == 'Value 45.0 in LLPL_LL not of data type 2SF. (Expected: 45)'

    assert error_list['AGS Format Rule 8'][1]['line'] == 71
    assert error_list['AGS Format Rule 8'][1]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 8'][1]['desc'] == 'Value 101 in LLPL_LL not of data type 2SF. (Expected: 100)'

    assert error_list['AGS Format Rule 8'][2]['line'] == 73
    assert error_list['AGS Format Rule 8'][2]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 8'][2]['desc'] == 'Value 0.2 in LLPL_PI not of data type 2SF. (Expected: 0.20)'


def test_rule_8_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][1]['line'] == 79
    assert error_list['AGS Format Rule 8'][1]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][1]['desc'] == 'Value 01-12-2020 in LOCA_START not in the ISO date/time format or is an invalid date/time.'

    assert error_list['AGS Format Rule 8'][2]['line'] == 80
    assert error_list['AGS Format Rule 8'][2]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][2]['desc'] == 'Value 2021-02-29 in LOCA_START not in the ISO date/time format or is an invalid date/time.'


def test_rule_8_5():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][0]['line'] == 76
    assert error_list['AGS Format Rule 8'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][0]['desc'] == 'Value 51:68:52.498 in LOCA_LAT not of data type DMS or is an invalid value.'

    assert error_list['AGS Format Rule 8'][1]['line'] == 77
    assert error_list['AGS Format Rule 8'][1]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][1]['desc'] == 'Value 51:28:152.498 in LOCA_LAT not of data type DMS or is an invalid value.'

    assert error_list['AGS Format Rule 8'][2]['line'] == 78
    assert error_list['AGS Format Rule 8'][2]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 8'][2]['desc'] == 'Value :28:152.498 in LOCA_LAT not of data type DMS or is an invalid value.'


def test_rule_8_6():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][3]['line'] == 85
    assert error_list['AGS Format Rule 8'][3]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][3]['desc'] == 'Value x in SAMP_RECL not of data type U. Numeric value expected.'


def test_rule_8_7():
    error_list = AGS4.check_file('tests/test_files/4.1-rule8-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 8' in error_list.keys()
    assert error_list['AGS Format Rule 8'][4]['line'] == 88
    assert error_list['AGS Format Rule 8'][4]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][4]['desc'] == 'Value xyz in SAMP_XXXX not of data type YN.'

    assert error_list['AGS Format Rule 8'][5]['line'] == 89
    assert error_list['AGS Format Rule 8'][5]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 8'][5]['desc'] == 'Value 10 in SAMP_XXXX not of data type YN.'


# def test_rule_9():
#    error_list = AGS4.check_file('tests/test_files/4.1-rule9.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')
#
#    assert 'AGS Format Rule 9' in error_list.keys()
#    # TODO assert error_list['AGS Format Rule 7'][0]['line'] == ?
#    assert error_list['AGS Format Rule 7'][0]['group'] == 'PROJ'
#    assert error_list['AGS Format Rule 7'][0]['desc'] == 'Headings not in order starting from FILE_FSET. Expected order: ...PROJ_MEMO|FILE_FSET'

def test_rule_9_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule9-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 9' in error_list.keys()
    assert error_list['AGS Format Rule 9'][0]['line'] == 78
    assert error_list['AGS Format Rule 9'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 9'][0]['desc'] == 'SAMP_XXXX not found in DICT table or the standard AGS4 dictionary.'


def test_rule_10_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10a' in error_list.keys()
    assert error_list['AGS Format Rule 10a'][0]['line'] == 73
    assert error_list['AGS Format Rule 10a'][1]['line'] == 74
    assert error_list['AGS Format Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 10a'][0]['desc'] == 'Duplicate key field combination: DATA|327-16A|15.00|15|U||1|15.00'


def test_rule_10_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10a' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 10a'][0]['line'] == ?
    assert error_list['AGS Format Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 10a'][0]['desc'] == 'Key field SAMP_ID not found.'


def test_rule_10_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10c' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 10c'][0]['line'] == ?
    assert error_list['AGS Format Rule 10c'][0]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 10c'][0]['desc'] == 'Parent entry for line not found in SAMP: 327-16A|15.00|15||'


def test_rule_10_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10c' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 10c'][0]['line'] == ?
    assert error_list['AGS Format Rule 10c'][0]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 10c'][0]['desc'] == 'Parent entry for line not found in SAMP: 327-16A|15.00|15|U|'


def test_rule_10_5():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10c' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 10c'][0]['line'] == ?
    assert error_list['AGS Format Rule 10c'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 10c'][0]['desc'] == 'Could not find parent group LOCA.'


def test_rule_10_6():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-6.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10b' in error_list.keys()
    assert error_list['AGS Format Rule 10b'][0]['line'] == 15
    assert error_list['AGS Format Rule 10b'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 10b'][0]['desc'] == 'Required field ABBR_DESC not found.'


def test_rule_11_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 11c' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 11c'][0]['line'] == ?
    assert error_list['AGS Format Rule 11c'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 11c'][0]['desc'] == 'Invalid record link: "ISPT|327-16A|2". No such record found.'


def test_rule_11_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 11c' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 11c'][0]['line'] == ?
    assert error_list['AGS Format Rule 11c'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 11c'][0]['desc'] == 'Invalid record link: "ISPT|327-16A|2.50". "@" should be used as delimiter.'


def test_rule_11_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 11c' not in error_list.keys()


def test_rule_12():
    error_list = AGS4.check_file('tests/test_files/4.1-rule12.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 10b' in error_list.keys()
    # TODO assert error_list['AGS Format Rule 10b'][0]['line'] == ?
    assert error_list['AGS Format Rule 10b'][0]['group'] == 'TRAN'
    assert error_list['AGS Format Rule 10b'][0]['desc'].startswith('Empty REQUIRED fields:')


def test_rule_13_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule13-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 13' in error_list.keys()
    assert error_list['AGS Format Rule 13'][0]['line'] == 6
    assert error_list['AGS Format Rule 13'][0]['group'] == 'PROJ'
    assert error_list['AGS Format Rule 13'][0]['desc'] == 'There should not be more than one DATA row in the PROJ table.'


def test_rule_13_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule13-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 13' in error_list.keys()
    assert error_list['AGS Format Rule 13'][0]['group'] == 'PROJ'
    assert error_list['AGS Format Rule 13'][0]['desc'] == 'PROJ table not found.'


def test_rule_14_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule14-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 14' in error_list.keys()
    assert error_list['AGS Format Rule 14'][0]['line'] == 25
    assert error_list['AGS Format Rule 14'][0]['group'] == 'TRAN'
    assert error_list['AGS Format Rule 14'][0]['desc'] == 'There should not be more than one DATA row in the TRAN table.'


def test_rule_14_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule14-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 14' in error_list.keys()
    assert error_list['AGS Format Rule 14'][0]['group'] == 'TRAN'
    assert error_list['AGS Format Rule 14'][0]['desc'] == 'TRAN table not found.'


def test_rule_14_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule14-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 17' in error_list.keys()
    assert error_list['AGS Format Rule 17'][0]['group'] == 'TYPE'
    assert error_list['AGS Format Rule 17'][0]['desc'] == 'Data type "YN" not found in TYPE table.'


def test_rule_15_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule15-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 15' in error_list.keys()
    assert error_list['AGS Format Rule 15'][0]['group'] == 'UNIT'
    assert error_list['AGS Format Rule 15'][0]['desc'] == 'UNIT table not found.'


def test_rule_15_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule15-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 15' in error_list.keys()
    assert error_list['AGS Format Rule 15'][0]['line'] == 47
    assert error_list['AGS Format Rule 15'][0]['group'] == 'UNIT'
    assert error_list['AGS Format Rule 15'][0]['desc'] == 'Unit "%" not found in UNIT table.'


def test_rule_16_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 16' in error_list.keys()
    assert error_list['AGS Format Rule 16'][0]['group'] == 'SAMP'
    assert error_list['AGS Format Rule 16'][0]['desc'] == '"U" under SAMP_TYPE in SAMP not found in ABBR table.'
    assert error_list['AGS Format Rule 16'][1]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 16'][1]['desc'] == '"U" under SAMP_TYPE in LLPL not found in ABBR table.'


def test_rule_16_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 16' in error_list.keys()
    assert error_list['AGS Format Rule 16'][0]['group'] == 'ABBR'
    assert error_list['AGS Format Rule 16'][0]['desc'] == 'ABBR table not found.'


def test_rule_16b_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16b-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 16' in error_list.keys()
    assert error_list['AGS Format Rule 16'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 16'][0]['desc'] == '"CP" under LOCA_TYPE in LOCA not found in ABBR table.'
    assert error_list['AGS Format Rule 16'][1]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 16'][1]['desc'] == '"RC" under LOCA_TYPE in LOCA not found in ABBR table.'


def test_rule_16b_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16b-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 16' in error_list.keys()
    assert error_list['AGS Format Rule 16'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 16'][0]['desc'] == '"CP " under LOCA_TYPE in LOCA not found in ABBR table.'
    assert error_list['AGS Format Rule 16'][1]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 16'][1]['desc'] == '" RC" under LOCA_TYPE in LOCA not found in ABBR table.'


def test_rule_16b_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16b-4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 11b' in error_list.keys()
    assert error_list['AGS Format Rule 11b'][0]['group'] == 'TRAN'
    assert error_list['AGS Format Rule 11b'][0]['desc'] == 'TRAN_RCON missing.'


def test_rule_16b_5():
    error_list = AGS4.check_file('tests/test_files/4.1-rule16b-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 11b' in error_list.keys()
    assert error_list['AGS Format Rule 11b'][0]['group'] == 'TRAN'
    assert error_list['AGS Format Rule 11b'][0]['desc'] == 'TRAN_RCON missing.'


def test_rule_17_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule17-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 17' in error_list.keys()
    assert error_list['AGS Format Rule 17'][0]['group'] == 'TYPE'
    assert error_list['AGS Format Rule 17'][0]['desc'] == 'Data type "ID" not found in TYPE table.'


def test_rule_17_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule17-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 17' in error_list.keys()
    assert error_list['AGS Format Rule 17'][0]['group'] == 'TYPE'
    assert error_list['AGS Format Rule 17'][0]['desc'] == 'TYPE table not found.'


def test_rule_18_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule18-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 9' in error_list.keys()
    assert error_list['AGS Format Rule 9'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 9'][0]['desc'] == 'LOCA_APPG not found in DICT table or the standard AGS4 dictionary.'


def test_rule_18_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule18-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 7' in error_list.keys()
    assert error_list['AGS Format Rule 7'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 7'][0]['desc'] == 'Headings not in order starting from LOCA_CHKG. Expected order: ...LOCA_APPG|LOCA_CHKG'


def test_rule_18_OK():
    error_list = AGS4.check_file('tests/test_files/4.1-rule18-OK.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 18' not in error_list.keys()


def test_rule_19():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 19' in error_list.keys()
    assert error_list['AGS Format Rule 19'][0]['group'] == 'TESTS'
    assert error_list['AGS Format Rule 19'][0]['desc'] == 'GROUP name should consist of four uppercase letters.'


def test_rule_19_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 19' in error_list.keys()
    assert error_list['AGS Format Rule 19'][0]['group'] == 'TST'
    assert error_list['AGS Format Rule 19'][0]['desc'] == 'GROUP name should consist of four uppercase letters.'
    assert error_list['AGS Format Rule 19b'][0]['group'] == 'TST'
    assert error_list['AGS Format Rule 19b'][0]['desc'] == 'Heading TST_DPTH should consist of a 4 character group name and a field name of up to 4 characters.'


def test_rule_19_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 19' in error_list.keys()
    assert error_list['AGS Format Rule 19'][0]['group'] == 'test'
    assert error_list['AGS Format Rule 19'][0]['desc'] == 'GROUP name should consist of four uppercase letters.'
    assert error_list['AGS Format Rule 19a'][0]['group'] == 'test'
    assert error_list['AGS Format Rule 19a'][0]['desc'] == 'Heading test_DPTH should consist of only uppercase letters, numbers, and an underscore character.'


def test_rule_19a_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19a-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 19a' in error_list.keys()
    assert error_list['AGS Format Rule 19a'][0]['group'] == 'TEST'
    assert error_list['AGS Format Rule 19a'][0]['desc'] == 'Heading TEST_DEPTH is more than 9 characters in length.'


def test_rule_19a_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19a-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 19a' in error_list.keys()
    assert error_list['AGS Format Rule 19a'][0]['group'] == 'TEST'
    assert error_list['AGS Format Rule 19a'][0]['desc'] == 'Heading TEST_D-H should consist of only uppercase letters, numbers, and an underscore character.'


def test_rule_19b_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19b-1.ags')

    assert 'AGS Format Rule 19b' in error_list.keys()
    assert error_list['AGS Format Rule 19b'][0]['group'] == 'DEMO'


def test_rule_19b_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule19b-2.ags')

    assert 'AGS Format Rule 19b' in error_list.keys()
    assert error_list['AGS Format Rule 19b'][2]['group'] == 'LLPL'
    assert error_list['AGS Format Rule 19b'][2]['desc'] == 'XXXX_425 does not start with the name of this group, nor is it defined in another group.'


def test_rule_20_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule20-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 20' in error_list.keys()
    assert error_list['AGS Format Rule 20'][0]['group'] == 'LOCA'
    assert error_list['AGS Format Rule 20'][0]['desc'] == 'FILE_FSET entry "327-16A" not found in FILE table.'
    assert error_list['AGS Format Rule 20'][1]['group'] == 'FILE'
    assert error_list['AGS Format Rule 20'][1]['desc'] == f'Sub-folder named "{os.path.join("FILE", "327")}" not found even though it is defined in the FILE table.'


def test_rule_20_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule20-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 20' in error_list.keys()
    assert error_list['AGS Format Rule 20'][0]['group'] == 'FILE'
    assert error_list['AGS Format Rule 20'][0]['desc'] == f'Sub-folder named "{os.path.join("FILE", "327")}" not found even though it is defined in the FILE table.'


def test_rule_20_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule20-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 20' in error_list.keys()
    assert error_list['AGS Format Rule 20'][0]['group'] == 'FILE'
    assert error_list['AGS Format Rule 20'][0]['desc'] == f'File named "{os.path.join("FILE", "327-16A", "wrong Report.pdf")}" not found even though it is defined in the FILE table.'


def test_rule_20_OK():
    error_list = AGS4.check_file('tests/test_files/4.1-rule20OK.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 20' not in error_list.keys()


def test_rule_LBSGCheck():
    error_list = AGS4.check_file('tests/test_files/LBSGCheck.ags')

    assert 'AGS Format Rule 10c' not in error_list.keys()

    assert 'Metadata' in error_list.keys()
    assert error_list['Metadata'][0]['desc'] == 'LBSGCheck.ags'
    assert error_list['Metadata'][2]['desc'] == f'python_ags4 v{__version__}'
    assert error_list['Metadata'][3]['desc'] == 'Standard_dictionary_v4_0_4.ags'


def test_rule_STNDandPREMCheck():
    error_list = AGS4.check_file('tests/test_files/STNDandPREMCheck.ags')

    assert 'AGS Format Rule 10c' not in error_list.keys()

    assert 'Metadata' in error_list.keys()
    assert error_list['Metadata'][0]['desc'] == 'STNDandPREMCheck.ags'
    assert error_list['Metadata'][2]['desc'] == f'python_ags4 v{__version__}'
    assert error_list['Metadata'][3]['desc'] == 'Standard_dictionary_v4_0_4.ags'


def test_rule_AGS3():
    error_list = AGS4.check_file('tests/test_files/AGS3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'AGS Format Rule 3' in error_list.keys()
    assert 'AGS3' in error_list['AGS Format Rule 3'][0]['desc']
