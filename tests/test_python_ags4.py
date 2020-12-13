import unittest
# import sys
# Prepend path so that AGS4.py is loaded from project file
# instead of current installation
# sys.path.insert(0, './')
from python_ags4 import AGS4


class Test_AGS4(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_AGS4_to_dict(self):
        data, headings = AGS4.AGS4_to_dict('tests/test_data.ags')

        self.assertEqual(data['PROJ']['PROJ_ID'][2], '123456')

    def test_AGS4_to_dataframe(self):
        data, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')

        self.assertEqual(data['LOCA'].loc[2, 'LOCA_ID'], 'Location_1')

    def test_convert_to_numeric(self):
        data, headings = AGS4.AGS4_to_dataframe('tests/test_data.ags')
        LOCA = AGS4.convert_to_numeric(data['LOCA'])

        self.assertEqual(LOCA.loc[0, 'LOCA_NATE'], 100000.01)


if __name__ == '__main__':
    unittest.main()
