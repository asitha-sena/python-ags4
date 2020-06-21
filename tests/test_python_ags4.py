#from python_ags4 import __version__
#
#
#def test_version():
#    assert __version__ == '0.1.0'


import unittest

import sys
sys.path.append('../')
from python_ags4 import AGS4

class Test_AGS4(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_AGS4_to_dict(self):
        data, headings = AGS4.AGS4_to_dict('test_data.ags')

        self.assertEqual(data['PROJ']['PROJ_ID'][2], '123456')

    def test_AGS4_to_dataframe(self):
        data, headings = AGS4.AGS4_to_dataframe('test_data.ags')

        self.assertEqual(data['LOCA'].loc[2, 'LOCA_ID'], 'Location_1')

    def test_convert_to_numeric(self):
        data, headings = AGS4.AGS4_to_dataframe('test_data.ags')
        LOCA = AGS4.convert_to_numeric(data['LOCA'])

        self.assertEqual(LOCA.loc[0, 'LOCA_NATE'], 100000.0)


if __name__ == '__main__':
    unittest.main()
