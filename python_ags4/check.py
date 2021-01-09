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

# Funtion to help store errors

def add_error_msg(ags_errors, rule, line, group, desc):
    '''Store AGS4 error in a dictionary.

    Parameters
    ----------
    ags_errors : dict
        Python dictionary to store details of errors in the AGS4 file being checked.
    rule : str
        Name/number of rule infringed.
    line : int
        Line number where error is located.
    group : str
        Name of GROUP in which error is located.
    desc : str
        Description of error.

    Returns
    -------
    dict
        Updated Python dictionary.

    '''

    try:
        ags_errors[rule].append({'line': line, 'group': group, 'desc': desc})

    except KeyError:
        ags_errors[rule] = []
        ags_errors[rule].append({'line': line, 'group': group, 'desc': desc})

    return ags_errors


# Line Rules

def rule_1(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 1: The file shall be entirely composed of ASCII characters.
    '''

    if line.isascii() is False:
        add_error_msg(ags_errors, 'Rule 1', line_number, '', 'Has Non-ASCII character(s).')

    return ags_errors


def rule_2a(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 2a: Each line should be delimited by a carriage return and line feed.
    '''

    if line[-2:] != '\r\n':
        add_error_msg(ags_errors, 'Rule 2a', line_number, '', 'Is not terminated by <CR> and <LF> characters.')

    return ags_errors


def rule_2c(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 2c: HEADING row should fully define the data. Therefore, it should not have duplicate fields.
    '''

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) != len(set(temp)):
            add_error_msg(ags_errors, 'Rule 2c', line_number, '', 'HEADER row has duplicate fields.')

    return ags_errors


def rule_3(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 3: Each line should be start with a data descriptor that defines its contents.
    '''

    if not line.isspace():
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if temp[0] not in ['GROUP', 'HEADING', 'TYPE', 'UNIT', 'DATA']:
            add_error_msg(ags_errors, 'Rule 3', line_number, '', 'Does not start with a valid data descriptor.')

    return ags_errors


def rule_4a(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 4a: A GROUP row should only contain the GROUP name as data
    '''

    if line.startswith('"GROUP"'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) > 2:
            add_error_msg(ags_errors, 'Rule 4a', line_number, temp[1], 'GROUP row has more than one field.')
        elif len(temp) < 2:
            add_error_msg(ags_errors, 'Rule 4a', line_number, '', 'GROUP row is malformed.')

    return ags_errors


def rule_4b(line, line_number=0, group='', headings=[], ags_errors={}):
    '''AGS4 Rule 4b: UNIT, TYPE, and DATA rows should have entries defined by the HEADING row.
    '''

    if line.strip('"').startswith(('UNIT', 'TYPE', 'DATA')):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(headings) == 0:
            # Avoid repetitions of same error by adding it only it is not already there
            try:

                if not any([(d['group'] == group) and (d['desc'] == 'Headings row missing.') for d in ags_errors['Rule 4b']]):
                    add_error_msg(ags_errors, 'Rule 4b', float('NaN'), group, 'Headings row missing.')

            except KeyError:
                add_error_msg(ags_errors, 'Rule 4b', float('NaN'), group, 'Headings row missing.')

        elif len(temp) != len(headings):
            add_error_msg(ags_errors, 'Rule 4b', line_number, group, 'Number of fields does not match the HEADING row.')

    return ags_errors


def rule_5(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 5: All fields should be enclosed in double quotes.
    '''

    if not line.isspace():
        if not line.startswith('"') or not line.strip('\r\n').endswith('"'):
            add_error_msg(ags_errors, 'Rule 5', line_number, '', 'Contains fields that are not enclosed in double quotes.')

        elif line.strip('"').startswith(('HEADING', 'UNIT', 'TYPE')):
            # If all fields are enclosed in double quotes then splitting by
            # ',' and '","' will return the same number of filelds
            if len(line.split('","')) != len(line.split(',')):
                add_error_msg(ags_errors, 'Rule 5', line_number, '', 'Contains fields that are not enclosed in double quotes.')

            # This check is not applied to DATA rows as it is possible that commas could be
            # present in fields with string data (i.e TYPE="X"). However, fields in DATA
            # rows that are not enclosed in double quotes will be caught by rule_4b() as
            # they will not be of the same length as the headings row after splitting by '","'.

    elif (line == '\r\n') or (line == '\n'):
        pass

    else:
        add_error_msg(ags_errors, 'Rule 5', line_number, '', 'Contains only spaces.')

    return ags_errors


def rule_6(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 6: All fields should be separated by commas and carriage returns are not
    allowed within a data field.
    '''

    # This will be satisfied if rule_2a, rule_4b and rule_5 are satisfied

    return ags_errors


def rule_19(line, line_number=0, ags_errors={}):
    '''AGS4 Rule 19: GROUP name should consist of four uppercase letters.
    '''

    if line.strip('"').startswith('GROUP'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            if (len(temp[1]) != 4) or not temp[1].isupper():
                add_error_msg(ags_errors, 'Rule 19', line_number, temp[1], 'GROUP name should consist of four uppercase letters.')

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
