from python_ags4 import AGS4, __version__
import pandas as pd


def test_rule_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 2' in error_list.keys()
    # TODO assert error_list['Rule 2'][0]['line'] == ?
    assert error_list['Rule 2'][0]['group'] == 'SAMP'
    assert error_list['Rule 2'][0]['desc'] == 'No DATA rows in group.'


def test_rule_2b_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 2b' in error_list.keys()
    # TODO assert error_list['Rule 2'][0]['line'] == ?
    assert error_list['Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['Rule 2b'][0]['desc'] == 'UNIT row missing from group.'


def test_rule_2b_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 2b' in error_list.keys()
    # TODO assert error_list['Rule 2b'][0]['line'] == ?
    assert error_list['Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['Rule 2b'][0]['desc'] == 'UNIT row missing from group.'

    # TODO assert error_list['Rule 2b'][0]['line'] == ?
    assert error_list['Rule 2b'][1]['group'] == 'ABBR'
    assert error_list['Rule 2b'][1]['desc'] == 'TYPE row missing from group.'


def test_rule_2b_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 2b' in error_list.keys()
    # TODO assert error_list['Rule 2b'][0]['line'] == ?
    assert error_list['Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['Rule 2b'][0]['desc'] == 'TYPE row missing from group.'


def test_rule_2b_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule2b4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 2b' in error_list.keys()
    # TODO assert error_list['Rule 2b'][0]['line'] == ?
    assert error_list['Rule 2b'][0]['group'] == 'ABBR'
    assert error_list['Rule 2b'][0]['desc'] == 'UNIT row is misplaced. It should be immediately below the HEADING row.'

    # TODO assert error_list['Rule 2b'][0]['line'] == ?
    assert error_list['Rule 2b'][1]['group'] == 'ABBR'
    assert error_list['Rule 2b'][1]['desc'] == 'TYPE row is misplaced. It should be immediately below the UNIT row.'


def test_rule_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 3' in error_list.keys()
    assert error_list['Rule 3'][0]['line'] == 58
    assert error_list['Rule 3'][0]['desc'] == 'Does not start with a valid data descriptor.'


def test_rule_7():
    error_list = AGS4.check_file('tests/test_files/4.1-rule7-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 7' in error_list.keys()
    # TODO assert error_list['Rule 7'][0]['line'] == ?
    assert error_list['Rule 7'][0]['group'] == 'PROJ'
    assert error_list['Rule 7'][0]['desc'] == 'Headings not in order starting from FILE_FSET. Expected order: ...PROJ_MEMO|FILE_FSET'


#def test_rule_9():
#    error_list = AGS4.check_file('tests/test_files/4.1-rule9.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')
#
#    assert 'Rule 9' in error_list.keys()
#    # TODO assert error_list['Rule 7'][0]['line'] == ?
#    assert error_list['Rule 7'][0]['group'] == 'PROJ'
#    assert error_list['Rule 7'][0]['desc'] == 'Headings not in order starting from FILE_FSET. Expected order: ...PROJ_MEMO|FILE_FSET'


def test_rule_10_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10a' in error_list.keys()
    # TODO assert error_list['Rule 10a'][0]['line'] == ?
    assert error_list['Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['Rule 10a'][0]['desc'] == 'Duplicate key field combination: DATA|327-16A|15.00|15|U||1|15.00'


def test_rule_10_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10a' in error_list.keys()
    # TODO assert error_list['Rule 10a'][0]['line'] == ?
    assert error_list['Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['Rule 10a'][0]['desc'] == 'Key field SAMP_ID not found.'


def test_rule_10_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10a' in error_list.keys()
    # TODO assert error_list['Rule 10a'][0]['line'] == ?
    assert error_list['Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['Rule 10a'][0]['desc'] == 'Parent entry for line not found in SAMP: 327-16A|15.00|15||'


def test_rule_10_4():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-4.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10a' in error_list.keys()
    # TODO assert error_list['Rule 10a'][0]['line'] == ?
    assert error_list['Rule 10a'][0]['group'] == 'LLPL'
    assert error_list['Rule 10a'][0]['desc'] == 'Parent entry for line not found in SAMP: 327-16A|15.00|15|U|'


def test_rule_10_5():
    error_list = AGS4.check_file('tests/test_files/4.1-rule10-5.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10c' in error_list.keys()
    # TODO assert error_list['Rule 10c'][0]['line'] == ?
    assert error_list['Rule 10c'][0]['group'] == 'SAMP'
    assert error_list['Rule 10c'][0]['desc'] == 'Could not find parent group LOCA.'


def test_rule_11_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 11c' in error_list.keys()
    # TODO assert error_list['Rule 11c'][0]['line'] == ?
    assert error_list['Rule 11c'][0]['group'] == 'SAMP'
    assert error_list['Rule 11c'][0]['desc'] == 'Invalid record link: "ISPT|327-16A|2". No such record found.'


def test_rule_11_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 11c' in error_list.keys()
    # TODO assert error_list['Rule 11c'][0]['line'] == ?
    assert error_list['Rule 11c'][0]['group'] == 'SAMP'
    assert error_list['Rule 11c'][0]['desc'] == 'Invalid record link: "ISPT|327-16A|2.50". "@" should be used as delimiter.'


def test_rule_11_3():
    error_list = AGS4.check_file('tests/test_files/4.1-rule11-3.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 11c' not in error_list.keys()


def test_rule_12():
    error_list = AGS4.check_file('tests/test_files/4.1-rule12.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 10b' in error_list.keys()
    # TODO assert error_list['Rule 10b'][0]['line'] == ?
    assert error_list['Rule 10b'][0]['group'] == 'TRAN'
    assert error_list['Rule 10b'][0]['desc'].startswith('Empty REQUIRED fields:')


def test_rule_13_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule13-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 13' in error_list.keys()
    assert error_list['Rule 13'][0]['group'] == 'PROJ'
    assert error_list['Rule 13'][0]['desc']  == 'There should not be more than one DATA row in the PROJ table.'


def test_rule_13_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule13-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 13' in error_list.keys()
    assert error_list['Rule 13'][0]['group'] == 'PROJ'
    assert error_list['Rule 13'][0]['desc']  == 'PROJ table not found.'


def test_rule_14_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule14-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 14' in error_list.keys()
    assert error_list['Rule 14'][0]['group'] == 'TRAN'
    assert error_list['Rule 14'][0]['desc']  == 'There should not be more than one DATA row in the TRAN table.'


def test_rule_14_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule14-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 14' in error_list.keys()
    assert error_list['Rule 14'][0]['group'] == 'TRAN'
    assert error_list['Rule 14'][0]['desc']  == 'TRAN table not found.'


def test_rule_15_1():
    error_list = AGS4.check_file('tests/test_files/4.1-rule15-1.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 15' in error_list.keys()
    assert error_list['Rule 15'][0]['group'] == 'UNIT'
    assert error_list['Rule 15'][0]['desc']  == 'UNIT table not found.'


def test_rule_15_2():
    error_list = AGS4.check_file('tests/test_files/4.1-rule15-2.ags', standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

    assert 'Rule 15' in error_list.keys()
    assert error_list['Rule 15'][0]['group'] == 'UNIT'
    assert error_list['Rule 15'][0]['desc']  == 'Unit "%" not found in UNIT table.'
