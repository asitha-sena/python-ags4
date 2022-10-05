import unittest

from python_ags4 import AGS4
from python_ags4.data import TEST_DATA

# TODO is this valid said @pedromorgan as a note ?

class Test_AGS4(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_AGS4_to_dict(self):
        data, headings = AGS4.AGS4_to_dict(TEST_DATA)

        self.assertEqual(data['PROJ']['PROJ_ID'][2], '123456')

    def test_AGS4_to_dataframe(self):
        data, headings = AGS4.AGS4_to_dataframe(TEST_DATA)

        self.assertEqual(data['LOCA'].loc[2, 'LOCA_ID'], 'Location_1')

    def test_convert_to_numeric(self):
        data, headings = AGS4.AGS4_to_dataframe(TEST_DATA)
        LOCA = AGS4.convert_to_numeric(data['LOCA'])

        self.assertEqual(LOCA.loc[0, 'LOCA_NATE'], 100000.01)


if __name__ == '__main__':
    unittest.main()
