
from python_ags4.ags4_cli import check, convert
from click.testing import CliRunner


TEST_FILE_WITHOUT_ERRORS = 'tests/test_files/4.1-rule20OK.ags'
TEST_FILE_WITH_ERRORS = 'tests/test_files/4.1-rule20-1.ags'


def test_check_file_with_errors():
    runner = CliRunner()
    result = runner.invoke(check, [TEST_FILE_WITH_ERRORS])

    assert result.exit_code == 1

    print(result.stdout)


def test_check_file_without_errors():
    runner = CliRunner()
    result = runner.invoke(check, [TEST_FILE_WITHOUT_ERRORS])

    assert result.exit_code == 0

    print(result.stdout)


def test_convert_ags_to_xlsx():
    runner = CliRunner()
    result = runner.invoke(convert, [TEST_FILE_WITH_ERRORS, 'tests/test_files/output.xlsx'])

    assert result.exit_code == 0

    print(result.stdout)
