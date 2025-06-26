from pandas.testing import assert_frame_equal
from python_ags4 import AGS4, utils


tables, headings = AGS4.AGS4_to_dataframe('tests/test_utils/benchmark.ags')


def test_get_DICT_table_from_json_file():

    DICT = utils.get_DICT_table_from_json_file('tests/test_utils/groupsandheadings.json')\
                .pipe(AGS4.convert_to_text, dictionary='4.1')

    assert_frame_equal(DICT, tables['DICT'], )


def test_get_ABBR_table_from_json_file():

    ABBR = utils.get_ABBR_table_from_json_file('tests/test_utils/abbreviations.json',
                                               'tests/test_utils/elrg_abbreviations.json',
                                               version='4.1')\
                .pipe(AGS4.convert_to_text, dictionary='4.1')

    assert_frame_equal(ABBR, tables['ABBR'])


def test_get_TYPE_table_from_json_file():

    TYPE = utils.get_TYPE_table_from_json_file('tests/test_utils/types.json', version='4.1')\
                .pipe(AGS4.convert_to_text, dictionary='4.1')

    assert_frame_equal(TYPE, tables['TYPE'])


def test_get_UNIT_table_from_json_file():

    UNIT = utils.get_UNIT_table_from_json_file('tests/test_utils/units.json', version='4.1')\
                .pipe(AGS4.convert_to_text, dictionary='4.1')

    assert_frame_equal(UNIT, tables['UNIT'])
