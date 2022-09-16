from pathlib import Path

from python_ags4 import AGS4


DATA_DIR = Path(__file__).parent

# Individual files
TEST_DATA = DATA_DIR / 'test_data.ags'


def load_test_data(*args, **kwargs):
    """Load test data.

    Note
    ----
    This wraps a call to ``AGS4.AGS4_to_dataframe``. All arguments and keyword arguments are passed directly to that method.

    """
    return AGS4.AGS4_to_dataframe(TEST_DATA, *args, **kwargs)
