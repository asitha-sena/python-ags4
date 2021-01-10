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


def combine_DICT_tables(input_files):
    '''Read multiple .ags files and cobmbine the DICT tables.

    If duplicate rows are encountered, the first will be kept and the rest dropped.
    Only 'HEADING','DICT_TYPE','DICT_GRP','DICT_HDNG' columns will be considered
    to determine duplicate rows. Precedence will be given to files in the order in
    which they appear in the input_files list.

    Parameters
    ----------
    input_files : list
        List of paths to .ags files.

    Returns
    -------
    DataFrame
        Pandas DataFrame with combined DICT tables.
    '''

    from pandas import DataFrame, concat
    from python_ags4.AGS4 import AGS4_to_dataframe
    import sys
    from rich import print as rprint

    # Initialize DataFrame to hold all dictionary entries
    master_DICT = DataFrame()

    for file in input_files:
        try:
            tables, _ = AGS4_to_dataframe(file)

            master_DICT = concat([master_DICT, tables['DICT']])

        except:
            pass

    # Check whether master_DICT is empty
    if master_DICT.shape[0] == 0:
        rprint('[red]  ERROR: No DICT tables available to proceed with checking.[/red]')
        rprint('[red]         Please ensure the input file has a DICT table or provide file with standard AGS4 dictionary.[/red]')
        sys.exit()

    # Drop duplicate entries
    master_DICT.drop_duplicates(['HEADING', 'DICT_TYPE', 'DICT_GRP', 'DICT_HDNG'], keep='first', inplace=True)

    return master_DICT


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
                    add_error_msg(ags_errors, 'Rule 4b', '-', group, 'Headings row missing.')

            except KeyError:
                add_error_msg(ags_errors, 'Rule 4b', '-', group, 'Headings row missing.')

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


def rule_19a(line, line_number=0, group='', ags_errors={}):
    '''AGS4 Rule 19a: HEADING names should consist of uppercase letters.
    '''

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            for item in temp[1:]:
                if not item.isupper() or (len(item) > 9):
                    add_error_msg(ags_errors, 'Rule 19a', line_number, group, f'Heading {item} should be uppercase and limited to 9 character in length.')

        else:
            add_error_msg(ags_errors, 'Rule 19a', line_number, group, 'Headings row does not seem to have any fields.')

    return ags_errors


def rule_19b(line, line_number=0, group='', ags_errors={}):
    '''AGS4 Rule 19b: HEADING names shall start with the group name followed by an underscore character.
    Where a HEADING referes to an existing HEADING within another GROUP, it shall bear the same name.
    '''

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            for item in temp[1:]:
                try:
                    if (len(item.split('_')[0]) != 4) or (len(item.split('_')[1]) > 4):
                        add_error_msg(ags_errors, 'Rule 19b', line_number, group, f'Heading {item} should consist of a 4 charater group name and a field name of upto 4 characters.')

                    # TODO: Check whether heading name is present in the standard AGS4 dictionary or in the DICT group in the input file

                except IndexError:
                    add_error_msg(ags_errors, 'Rule 19b', line_number, group, f'Heading {item} should consist of group name and field name separated by "_".')

    return ags_errors


# Group Rules

def rule_2(tables, headings, ags_errors={}):
    '''AGS4 Rule 2: Each file should consist of one or more GROUPs and each GROUP should
    consist of one or more DATA rows.
    '''

    for key in tables:
        # Re-index table to ensure row numbering starts from zero
        tables[key].reset_index(drop=True, inplace=True)

        # Check if there is a UNIT row in the table
        # NOTE: .tolist() used instead of .values to avoid "FutureWarning: elementwise comparison failed."
        #       ref: https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        if 'DATA' not in tables[key]['HEADING'].tolist():
            add_error_msg(ags_errors, 'Rule 2', '-', key, 'No DATA rows in group.')

    return ags_errors


def rule_2b(tables, headings, ags_errors={}):
    '''AGS4 Rule 2b: UNIT and TYPE rows should be defined at the start of each GROUP
    '''

    for key in tables:
        # Re-index table to ensure row numbering starts from zero
        tables[key].reset_index(drop=True, inplace=True)

        # Check if there is a UNIT row in the table
        # NOTE: .tolist() used instead of .values to avoid "FutureWarning: elementwise comparison failed."
        #       ref: https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        if 'UNIT' not in tables[key]['HEADING'].tolist():
            add_error_msg(ags_errors, 'Rule 2b', '-', key, 'UNIT row missing from group.')

        # Check if the UNIT row is in the correct location within the table
        elif tables[key].loc[0, 'HEADING'] != 'UNIT':
            add_error_msg(ags_errors, 'Rule 2b', '-', key, 'UNIT row is misplaced. It should be immediately below the HEADING row.')

        # Check if there is a TYPE row in the table
        if 'TYPE' not in tables[key]['HEADING'].tolist():
            add_error_msg(ags_errors, 'Rule 2b', '-', key, 'TYPE row missing from group.')

        # Check if the UNIT row is in the correct location within the table
        elif tables[key].loc[1, 'HEADING'] != 'TYPE':
            add_error_msg(ags_errors, 'Rule 2b', '-', key, 'TYPE row is misplaced. It should be immediately below the UNIT row.')

    return ags_errors


def rule_7(headings, dictionary, ags_errors={}):
    '''AGS4 Rule 7: HEADINGs shall be in the order described in the AGS4 dictionary.
    '''

    for key in headings:
        # Extract list of headings defined for the group in the dictionaries
        mask = dictionary.DICT_GRP == key
        reference_headings_list = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        # Verify that all headings names in the group are defined in the dictionaries
        if set(headings[key][1:]).issubset(set(reference_headings_list)):

            # Make a copy of reference list to modify
            temp = reference_headings_list.copy()

            for item in reference_headings_list:
                # Drop heading names that are not used in the file
                if item not in headings[key]:
                    temp.remove(item)

            # Finally compare the two lists. They will be identical only if all element are in the same order
            if not temp == headings[key][1:]:
                msg = f'HEADING names in {key} are not in the order that they are defined in the DICT table and the standard dictionary.'
                add_error_msg(ags_errors, 'Rule 7', '-', key, msg)

        else:
            pass

    return ags_errors


def rule_9(headings, dictionary, ags_errors={}):
    '''AGS4 Rule 9: GROUP and HEADING names will be taken from the standard AGS4 dictionary or
    defined in DICT table in the .ags file.
    '''

    for key in headings:
        for item in headings[key][1:]:
            mask = dictionary.DICT_GRP == key

            if item not in dictionary.loc[mask, 'DICT_HDNG'].tolist():
                add_error_msg(ags_errors, 'Rule 9', '-', key, f'{item} not found in DICT table or the provided standard AGS4 dictionary.')

    return ags_errors


def rule_10a(tables, headings, dictionary, ags_errors={}):
    '''AGS4 Rule 10a: KEY fields in a GROUP must be present (even if null). There should not be any dupliate KEY field combinations.
    '''

    for group in tables:
        # Extract KEY fields from dictionary
        mask = (dictionary.DICT_GRP == group) & (dictionary.DICT_STAT.str.contains('key', case=False))
        key_fields = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        # Check for missing KEY fields
        for heading in key_fields:
            if heading not in headings[group]:
                add_error_msg(ags_errors, 'Rule 10a', '-', group, f'Key field {heading} not found.')

        # Check for duplicate KEY field combinations if all KEY fields are present
        if set(key_fields).issubset(set(headings[group])):
            #'HEADING' column has to added explicity as it is not in the key field list
            key_fields = ['HEADING'] + key_fields

            mask = tables[group].duplicated(key_fields, keep=False)
            duplicate_rows = tables[group].loc[mask, :]

            for i, row in duplicate_rows.iterrows():
                duplicate_key_combo = '|'.join(row[key_fields].tolist())
                add_error_msg(ags_errors, 'Rule 10a', '-', group, f'Duplicate key field combination: {duplicate_key_combo}')

    return ags_errors
