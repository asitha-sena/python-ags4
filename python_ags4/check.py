# Copyright (C) 2020  Asitha Senanayake
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# https://github.com/asitha-sena/python-ags4


# Line Rules

def rule_1(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 1: The file shall be entirely composed of ASCII characters.
    '''

    # Create dictionary to store Rule 1 infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 1']
    except KeyError:
        ags_errors['Rule 1'] = {}
        ags_errors['Rule 1']['msg'] = 'Non-ASCII character in line.'
        ags_errors['Rule 1']['line_number'] = []

    # Assert that input line conforms to Rule 1
    try:
        assert line.isascii() is True
    except AssertionError:
        ags_errors['Rule 1']['line_number'].append(line_number)

    return ags_errors


def rule_2a(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 2a: Each line should be delimited by a carriage return and line feed.
    '''

    # Create dictionary to store Rule 2a infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 2a']
    except KeyError:
        ags_errors['Rule 2a'] = {}
        ags_errors['Rule 2a']['msg'] = 'Line not terminated with /r/n.'
        ags_errors['Rule 2a']['line_number'] = []

    # Assert that input line conforms to Rule 2a
    try:
        assert line[-2:] == '\r\n'
    except AssertionError:
        ags_errors['Rule 2a']['line_number'].append(line_number)

    return ags_errors


def rule_2c(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 2c: HEADING row should fully define the data. Therefore, it should not have duplicate fields.
    '''

    # Create dictionary to store Rule 2c infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 2c']
    except KeyError:
        ags_errors['Rule 2c'] = {}
        ags_errors['Rule 2c']['msg'] = 'HEADER row has duplicate fields.'
        ags_errors['Rule 2c']['line_number'] = []

    # Assert that input line conforms to Rule 2c
    if line.startswith("HEADING"):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        try:
            assert len(temp) == len(set(temp))

        except AssertionError:
            ags_errors['Rule 2c']['line_number'].append(line_number)

    return ags_errors


def rule_3(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 3: Each line should be start with a data descriptor that defines its contents.
    '''

    # Create dictionary to store Rule 3 infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 3']
    except KeyError:
        ags_errors['Rule 3'] = {}
        ags_errors['Rule 3']['msg'] = 'Line does not start with a valid data descriptor.'
        ags_errors['Rule 3']['line_number'] = []

    # Assert that input line conforms to Rule 3
    if not line.isspace():
        try:
            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            assert temp[0] in ["GROUP", "HEADING", "TYPE", "UNIT", "DATA"]

        except AssertionError:
            ags_errors['Rule 3']['line_number'].append(line_number)

    return ags_errors


def rule_4a(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 4a: A GROUP row should only contain the GROUP name as data
    '''

    # Create dictionary to store Rule 4a infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 4a']
    except KeyError:
        ags_errors['Rule 4a'] = {}
        ags_errors['Rule 4a']['msg'] = 'The GROUP name missing or too many data fields present.'
        ags_errors['Rule 4a']['line_number'] = []

    # Assert that input line conforms to Rule 4a
    if line.startswith('"GROUP"'):
        try:
            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            assert len(temp) == 2

        except AssertionError:
            ags_errors['Rule 4a']['line_number'].append(line_number)

    return ags_errors


def rule_5(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 5: All fields should be enclosed in double quotes.
    '''

    # Create dictionary to store Rule 5 infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 5']
    except KeyError:
        ags_errors['Rule 5'] = {}
        ags_errors['Rule 5']['msg'] = 'Line contains fields that are not enclosed in double quotes.'
        ags_errors['Rule 5']['line_number'] = []

    # Assert that input line conforms to Rule 5
    if not line.isspace():
        try:
            assert line.startswith('"')
            assert line.strip('\r\n').endswith('"')

        except AssertionError:
            ags_errors['Rule 5']['line_number'].append(line_number)

    if line.startswith("HEADING") | line.startswith("UNIT") | line.startswith("TYPE"):
        try:
            # If all fields are enclosed in double quotes then splitting by
            # ',' and '","' will return the same number of filelds
            assert len(line.split('","')) == len(line.split(','))

            # This check is not applied to DATA rows as it is possible that commas could be
            # present in fields with string data (i.e TYPE="X"). However, fields in DATA
            # rows that are not enclosed in double quotes will be caught by rule_4b() as
            # they will not be of the same length as the headings row after splitting by '","'.

        except AssertionError:
            ags_errors['Rule 5']['line_number'].append(line_number)

    return ags_errors


def rule_6(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 6: All fields should be separated by commas and carriage returns are not
    allowed within a data field.
    '''

    # This will be satisfied if rule_2a, rule_4b and rule_5 are satisfied

    return ags_errors


def rule_19(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 19: A GROUP row should only contain the GROUP name as data
    '''

    # Create dictionary to store Rule 19 infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 19']
    except KeyError:
        ags_errors['Rule 19'] = {}
        ags_errors['Rule 19']['line_number'] = []

    # Assert that input line conforms to Rule 19
    if line.startswith('"GROUP"'):
        try:
            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            assert len(temp) == 2

        except AssertionError:
            ags_errors['Rule 19']['line_number'].append(line_number)

    return ags_errors


# Group Rules

def rule_2(tables, headings, ags_errors={}):
    '''AGS4 Rule 2: Each file should consist of one or more GROUPs and each GROUP should
    consist of one or more DATA rows.
    '''

    # Create dictionary to store Rule 2 infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 2']
    except KeyError:
        ags_errors['Rule 2'] = {}
        ags_errors['Rule 2']['msg'] = 'GROUP does not have any DATA rows.'
        ags_errors['Rule 2']['group'] = []

    # Assert that input tables conforms to Rule 2
    for key in tables:
        try:
            assert "DATA" in tables[key]['HEADING'].values
        except AssertionError:
            ags_errors['Rule 2']['group'].append(key)

    return ags_errors


def rule_2b(tables, headings, ags_errors={}):
    '''AGS4 Rule 2b: UNIT and TYPE rows should be defined at the start of each GROUP
    '''

    # Create dictionary to store Rule 2b infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 2b']
    except KeyError:
        ags_errors['Rule 2b'] = {}
        ags_errors['Rule 2b']['msg'] = 'Missing or misplaced UNIT/TYPE row(s). UNIT and TYPE rows should immediately follow the HEADING row.'
        ags_errors['Rule 2b']['group'] = []

    # Assert that input tables conforms to Rule 2b
    for key in tables:
        # Re-index table to ensure row numbering starts from zero
        tables[key].reset_index(drop=True, inplace=True)

        try:
            assert "UNIT" in tables[key].loc[0, 'HEADING'] == "UNIT"
            assert "TYPE" in tables[key].loc[1, 'HEADING'] == "TYPE"

        except AssertionError:
            ags_errors['Rule 2b']['group'].append(key)

    return ags_errors


def rule_4b(line, line_number=0, headings=[], ags_errors={}):
    '''AGS4 Rule 4b: UNIT, TYPE, and DATA rows should have entries defined by the HEADING row.
    '''

    # Create dictionary to store Rule 4b infractions within the main ags_errors dictionary
    try:
        ags_errors['Rule 4b']
    except KeyError:
        ags_errors['Rule 4b'] = {}
        ags_errors['Rule 4b']['line_number'] = []

    # Assert that input line conforms to Rule 4b
    try:
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if temp[0] in ["UNIT", "TYPE", "DATA"]:
            assert len(temp) == len(headings[key])

    except AssertionError:
        ags_errors['Rule 4b']['line_number'].append(line_number)

    return ags_errors
