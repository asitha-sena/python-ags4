# Copyright (C) 2020-2022  Asitha Senanayake
#
# This file is part of python_ags4.
#
# python_ags4 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# https://github.com/asitha-sena/python-ags4
# https://gitlab.com/ags-data-format-wg/ags-python-library


# Helper functions

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


def combine_DICT_tables(*ags_tables):
    '''Combine DICT tables

    If duplicate rows are encountered, the first will be kept and the rest dropped.
    Only 'HEADING','DICT_TYPE','DICT_GRP','DICT_HDNG' columns will be considered
    to determine duplicate rows. Precedence will be given to files in the order in
    which they appear in the input_files list.
    IMPORTANT: The standard AGS4 dictionary has to be the first entry in order for
    order of headings (AGS Format Rule 7) to checked correctly.

    Parameters
    ----------
    ags_tables : dictionary of Pandas DataFrames
        A dictionary of Pandas DataFrames containing data from a .ags file that is
        output from the AGS4_to_dataframe() function

    Returns
    -------
    DataFrame
        Pandas DataFrame with combined DICT tables.
    '''

    from pandas import DataFrame, concat
    from .AGS4 import AGS4Error
    from rich import print as rprint

    # Initialize DataFrame to hold all dictionary entries
    master_DICT = DataFrame()

    for item in ags_tables:
        try:

            master_DICT = concat([master_DICT, item['DICT']])

        except KeyError:
            # KeyError if there is no DICT table in an input file
            rprint('[yellow]  WARNING: DICT table not found in input file.[/yellow]')

    # Check whether master_DICT is empty
    if master_DICT.shape[0] == 0:
        rprint('[red]  ERROR: No DICT tables available to proceed with checking.[/red]')
        rprint('[red]         Please ensure the input file has a DICT table or provide file with standard AGS4 dictionary.[/red]')
        raise AGS4Error("No DICT tables available to proceed with checking. "
                        "Please ensure the input file has a DICT table or provide file with standard AGS4 dictionary.")


    # Drop duplicate entries
    master_DICT.drop_duplicates(['HEADING', 'DICT_TYPE', 'DICT_GRP', 'DICT_HDNG'], keep='first', inplace=True)

    return master_DICT


def fetch_record(record_link, tables):
    '''Check whether record link points to an existing entry

    Parameters
    ----------
    record_link : list
        AGS4 Record Link (i.e. TYPE = "RL") converted to an ordered list
    tables : dict
        Dictionary of Pandas DataFrames with all AGS4 data in file

    Returns
    -------
    DataFrame
    '''

    from pandas import DataFrame
    from pandas.errors import MergeError

    try:
        # Get name(s) of GROUP and KEY fields
        group = record_link[0]
        field_names = tables[group].columns.tolist()[1:]

        # Convert record link to dataframe
        df1 = DataFrame(record_link[1:]).T

        # Assign heading names to columns
        df1.columns = field_names[0:len(record_link)-1]

        # Use merge operation to check whether record link matches with entry
        # in the linked tables
        df2 = df1.merge(tables[group].filter(regex=r'[^HEADING]'), how='left', indicator=True).query(''' _merge=="both" ''')

        return df2.filter(regex=r'[^_merge]')

    except IndexError:
        # Record link list may be empty
        return DataFrame()

    except KeyError:
        # group not in tables
        return DataFrame()

    except ValueError:
        # Input record link has more entries than there are columns in the table to which it refers
        return DataFrame()

    except MergeError:
        # No common columns on which to perform merge operation
        return DataFrame()


def pick_standard_dictionary(tables=None, dict_version=None):
    '''Pick standard dictionary to check file.

    Parameters
    ----------
    tables : dict
        Dictionary of Pandas DataFrames with all AGS4 data in file
    dict_version : str, optional
        String with version number to override TRAN_AGS. Should be one of
        '4.1.1', 4.1', '4.0.4', 4.0.3', '4.0'.

    Returns
    -------
    str
      File path to standard dictionary
    '''

    import pkg_resources
    from rich import print as rprint

    # Select standard dictionary based on TRAN_AGS
    try:
        if dict_version not in ['4.1.1', '4.1', '4.0.4', '4.0.3', '4.0']:
            TRAN = tables['TRAN']
            dict_version = TRAN.loc[TRAN.HEADING.eq('DATA'), 'TRAN_AGS'].values[0]

        if dict_version == '4.0.3':
            path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_0_3.ags')
        elif dict_version.startswith('4.0'):
            path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_0_4.ags')
        elif dict_version == '4.1':
            path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1.ags')
        elif dict_version == '4.1.1':
            path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1_1.ags')
        else:
            rprint('[yellow]  WARNING: Standard dictionary for AGS4 version specified in TRAN_AGS not available.[/yellow]')
            rprint('[yellow]           Defaulting to standard dictionary v4.1.1.[/yellow]')
            path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1_1.ags')

    except KeyError:
        # TRAN table not in file
        rprint('[yellow]  WARNING: TRAN_AGS not found. Defaulting to standard dictionary v4.1.1.[/yellow]')
        path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1_1.ags')

    except IndexError:
        # No DATA rows in TRAN table
        rprint('[yellow]  WARNING: TRAN_AGS not found. Defaulting to standard dictionary v4.1.1.[/yellow]')
        path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1_1.ags')

    except TypeError:
        # TRAN table not found and dict_version not valid
        rprint('[yellow]  WARNING: Neither TRAN_AGS nor dict_version is valid. Defaulting to standard dictionary v4.1.1.[/yellow]')
        path_to_standard_dictionary = pkg_resources.resource_filename('python_ags4', 'Standard_dictionary_v4_1_1.ags')

    return path_to_standard_dictionary


def add_meta_data(input_file, standard_dictionary, ags_errors={}):
    '''Add meta data from input file to error list.

    Parameters
    ----------
    input_file : str
        Path to input file
    standard_dictionary : str
        Path to standard dictionary file
    ags_errors : dict
        Python dictionary to store details of errors in the AGS4 file being checked.

    Returns
    -------
    dict
        Updated Python dictionary.
    '''

    import os
    from python_ags4 import __version__
    from datetime import datetime

    add_error_msg(ags_errors, 'Metadata', 'File Name', '', f'{os.path.basename(input_file)}')
    add_error_msg(ags_errors, 'Metadata', 'File Size', '', f'{int(os.path.getsize(input_file)/1024)} kB')
    add_error_msg(ags_errors, 'Metadata', 'Checker', '', f'python_ags4 v{__version__}')

    if standard_dictionary is not None:
        add_error_msg(ags_errors, 'Metadata', 'Dictionary', '', f'{os.path.basename(standard_dictionary)}')

    add_error_msg(ags_errors, 'Metadata', 'Time (UTC)', '', f'{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}')

    return ags_errors


# Line Rules

def rule_1(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 1: The file shall be entirely composed of ASCII characters.
    '''

    if line.isascii() is False:
        add_error_msg(ags_errors, 'AGS Format Rule 1', line_number, '', 'Has Non-ASCII character(s).')

    return ags_errors


def rule_2a(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 2a: Each line should be delimited by a carriage return and line feed.
    '''

    if line[-2:] != '\r\n':
        add_error_msg(ags_errors, 'AGS Format Rule 2a', line_number, '', 'Is not terminated by <CR> and <LF> characters.')

    return ags_errors


def rule_3(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 3: Each line should be start with a data descriptor that defines its contents.
    '''

    if not line.isspace():
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if temp[0] not in ['GROUP', 'HEADING', 'TYPE', 'UNIT', 'DATA']:
            add_error_msg(ags_errors, 'AGS Format Rule 3', line_number, '', 'Does not start with a valid data descriptor.')

    return ags_errors


def rule_4_1(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 4: A GROUP row should only contain the GROUP name as data
    '''

    if line.startswith('"GROUP"'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) > 2:
            add_error_msg(ags_errors, 'AGS Format Rule 4', line_number, temp[1], 'GROUP row has more than one field.')
        elif len(temp) < 2:
            add_error_msg(ags_errors, 'AGS Format Rule 4', line_number, '', 'GROUP row is malformed.')

    return ags_errors


def rule_4_2(line, line_number=0, group='', headings=[], ags_errors={}):
    '''AGS Format Rule 4: UNIT, TYPE, and DATA rows should have entries defined by the HEADING row.
    '''

    if line.strip('"').startswith(('UNIT', 'TYPE', 'DATA')):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(headings) == 0:
            # Avoid repetitions of same error by adding it only it is not already there
            try:

                if not any([(d['group'] == group) and (d['desc'] == 'Headings row missing.') for d in ags_errors['AGS Format Rule 4']]):
                    add_error_msg(ags_errors, 'AGS Format Rule 4', '-', group, 'Headings row missing.')

            except KeyError:
                add_error_msg(ags_errors, 'AGS Format Rule 4', '-', group, 'Headings row missing.')

        elif len(temp) != len(headings):
            add_error_msg(ags_errors, 'AGS Format Rule 4', line_number, group, 'Number of fields does not match the HEADING row.')

    return ags_errors


def rule_5(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 5: All fields should be enclosed in double quotes.
    '''

    import re

    if not line.isspace():
        if not line.startswith('"') or not line.strip('\r\n').endswith('"'):
            add_error_msg(ags_errors, 'AGS Format Rule 5', line_number, '', 'Contains fields that are not enclosed in double quotes.')

        elif line.strip('"').startswith(('HEADING', 'UNIT', 'TYPE')):
            # If all fields are enclosed in double quotes then splitting by
            # ',' and '","' will return the same number of filelds
            if len(line.split('","')) != len(line.split(',')):
                add_error_msg(ags_errors, 'AGS Format Rule 5', line_number, '', 'Contains fields that are not enclosed in double quotes.')

            # This check is not applied to DATA rows as it is possible that commas could be
            # present in fields with string data (i.e TYPE="X"). However, fields in DATA
            # rows that are not enclosed in double quotes will be caught by rule_4b() as
            # they will not be of the same length as the headings row after splitting by '","'.

        else:
            # Verify that quotes within data fields are enclosed by a second double quote

            # Remove quotes enclosing data fields
            temp = re.sub(r'","', ' ', line.strip('\r\n')).strip(r'"')
            # Remove correct double-double quotes
            temp = re.sub(r'""', ' ', temp)

            # Find orphan double quotes
            if '"' in re.findall(r'"', temp):
                msg = 'Contains quotes within a data field. All such quotes should be enclosed by a second quote.'
                add_error_msg(ags_errors, 'AGS Format Rule 5', line_number, '', msg)

    elif (line == '\r\n') or (line == '\n'):
        pass

    else:
        add_error_msg(ags_errors, 'AGS Format Rule 5', line_number, '', 'Contains only spaces.')

    return ags_errors


def rule_6(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 6: All fields should be separated by commas and carriage returns are not
    allowed within a data field.
    '''

    # This will be satisfied if rule_2a, rule_4b and rule_5 are satisfied

    return ags_errors


def rule_7_1(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 7: HEADINGs shall be in the order described in the AGS4 dictionary.
    Therefore, it should not have duplicated headings.
    '''

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) != len(set(temp)):
            add_error_msg(ags_errors, 'AGS Format Rule 7', line_number, '', 'HEADER row has duplicate fields.')

    return ags_errors


def rule_19(line, line_number=0, ags_errors={}):
    '''AGS Format Rule 19: GROUP name should consist of four uppercase letters.
    '''

    if line.strip('"').startswith('GROUP'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            if (len(temp[1]) != 4) or not temp[1].isupper():
                add_error_msg(ags_errors, 'AGS Format Rule 19', line_number, temp[1], 'GROUP name should consist of four uppercase letters.')

    return ags_errors


def rule_19a(line, line_number=0, group='', ags_errors={}):
    '''AGS Format Rule 19a: HEADING names should consist of uppercase letters.
    '''

    import re

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            for item in temp[1:]:
                if len(re.findall(r'[^A-Z0-9_]', item)) > 0:
                    msg = f'Heading {item} should consist of only uppercase letters, numbers, and an underscore character.'
                    add_error_msg(ags_errors, 'AGS Format Rule 19a', line_number, group, msg)

                if len(item) > 9:
                    msg = f'Heading {item} is more than 9 characters in length.'
                    add_error_msg(ags_errors, 'AGS Format Rule 19a', line_number, group, msg)

        else:
            add_error_msg(ags_errors, 'AGS Format Rule 19a', line_number, group, 'Headings row does not seem to have any fields.')

    return ags_errors


def rule_19b_1(line, line_number=0, group='', ags_errors={}):
    '''AGS Format Rule 19b: HEADING names shall start with the group name followed by an underscore character.
    Where a HEADING refers to an existing HEADING within another GROUP, it shall bear the same name.
    '''

    if line.strip('"').startswith('HEADING'):
        temp = line.rstrip().split('","')
        temp = [item.strip('"') for item in temp]

        if len(temp) >= 2:
            for item in temp[1:]:
                try:
                    if (len(item.split('_')[0]) != 4) or (len(item.split('_')[1]) > 4):
                        msg = f'Heading {item} should consist of a 4 character group name and a field name of up to 4 characters.'
                        add_error_msg(ags_errors, 'AGS Format Rule 19b', line_number, group, msg)

                except IndexError:
                    msg = f'Heading {item} should consist of group name and field name separated by "_".'
                    add_error_msg(ags_errors, 'AGS Format Rule 19b', line_number, group, msg)

    return ags_errors


# Group Rules

def rule_2(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 2: Each file should consist of one or more GROUPs and each GROUP should
    consist of one or more DATA rows.
    '''

    for key in tables:
        # Re-index table to ensure row numbering starts from zero
        tables[key].reset_index(drop=True, inplace=True)

        # Check if there is a UNIT row in the table
        # NOTE: .tolist() used instead of .values to avoid "FutureWarning: element-wise comparison failed."
        #       ref: https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        if 'DATA' not in tables[key]['HEADING'].tolist():
            line_number = line_numbers[key]['GROUP']
            add_error_msg(ags_errors, 'AGS Format Rule 2', line_number, key, 'No DATA rows in group.')

    return ags_errors


def rule_2b(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 2b: UNIT and TYPE rows should be defined at the start of each GROUP
    '''

    for key in tables:
        # Re-index table to ensure row numbering starts from zero
        tables[key].reset_index(drop=True, inplace=True)

        # Check if there is a UNIT row in the table
        # NOTE: .tolist() used instead of .values to avoid "FutureWarning: elementwise comparison failed."
        #       ref: https://stackoverflow.com/questions/40659212/futurewarning-elementwise-comparison-failed-returning-scalar-but-in-the-futur
        if 'UNIT' not in tables[key]['HEADING'].tolist():
            line_number = line_numbers[key]['GROUP']
            add_error_msg(ags_errors, 'AGS Format Rule 2b', line_number, key, 'UNIT row missing from group.')

        # Check if the UNIT row is in the correct location within the table
        elif tables[key].loc[0, 'HEADING'] != 'UNIT':
            line_number = int(tables[key].loc[tables[key]['HEADING'] == 'UNIT', 'line_number'].values[0])
            # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
            # that Pandas returns by default
            msg = 'UNIT row is misplaced. It should be immediately below the HEADING row.'
            add_error_msg(ags_errors, 'AGS Format Rule 2b', line_number, key, msg)

        # Check if there is a TYPE row in the table
        if 'TYPE' not in tables[key]['HEADING'].tolist():
            line_number = line_numbers[key]['GROUP']
            add_error_msg(ags_errors, 'AGS Format Rule 2b', line_number, key, 'TYPE row missing from group.')

        # Check if the UNIT row is in the correct location within the table
        elif tables[key].loc[1, 'HEADING'] != 'TYPE':
            line_number = int(tables[key].loc[tables[key]['HEADING'] == 'TYPE', 'line_number'].values[0])
            # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
            # that Pandas returns by default
            add_error_msg(ags_errors, 'AGS Format Rule 2b', line_number, key, 'TYPE row is misplaced. It should be immediately below the UNIT row.')

    return ags_errors


def rule_7_2(headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 7: HEADINGs shall be in the order described in the AGS4 dictionary.
    '''

    for key in headings:
        # Extract list of headings defined for the group in the dictionaries
        mask = dictionary.DICT_GRP == key
        reference_headings_list = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        # Pick list of headings in current table not including 'HEADING' and 'line_number'
        headings_list = [x for x in headings[key] if x not in ['HEADING', 'line_number']]

        # Verify that all headings names in the group are defined in the dictionaries
        if set(headings_list).issubset(set(reference_headings_list)):

            # Make a copy of reference list with only items that have been used
            temp = [x for x in reference_headings_list if x in headings_list]

            for i, item in enumerate(headings_list):
                if item != temp[i]:
                    line_number = line_numbers[key]['HEADING']
                    msg = f'Headings not in order starting from {item}. Expected order: ...{"|".join(temp[i:])}'
                    add_error_msg(ags_errors, 'AGS Format Rule 7', line_number, key, msg)

                    return ags_errors

        else:
            line_number = line_numbers[key]['HEADING']
            msg = 'Order of headings could not be checked as one or more fields were not found in either the DICT table or the standard dictionary. '\
                  'Check error log under AGS Format Rule 9.'
            add_error_msg(ags_errors, 'AGS Format Rule 7', line_number, key, msg)

    return ags_errors


def rule_8(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 8: Data variables shall be presented in units of measurements
    and type that are described by the appropriate data field UNIT and data
    field TYPE defined at the start of the GROUP.
    '''

    import pandas as pd
    from python_ags4.AGS4 import format_numeric_column

    for group in tables:
        # First make copy of table to avoid unexpected side-effects
        df = tables[group].copy()

        try:
            # Create dictionary of data types in table
            data_types = df.filter(regex=r'[^line_number]').loc[df.HEADING.eq('TYPE'), :].to_dict('records')[0]

            for col, data_type in data_types.items():
                if 'DP' in data_type:
                    i = int(data_type.strip('DP'))

                    if i == 0:
                        mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].str.match(r'^-?\d+\.?$')
                    else:
                        mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].str.match(f'^-?\\d+\\.\\d{{{i}}}$')

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not of data type {data_type}.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif 'SCI' in data_type:
                    i = int(data_type.strip('SCI'))
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].str.match(f'^-?\\d\\.\\d{{{i}}}[eE][+-]?\\d+$')

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not of data type {data_type}.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif 'SF' in data_type:
                    i = int(data_type.strip('SF'))

                    # Convert column to numeric values and convert back to correctly formatted strings
                    df['temp'] = pd.to_numeric(df[col], errors='coerce')
                    df = format_numeric_column(df, 'temp', data_type)

                    # Compare correctly formatted strings with original strings
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].eq(df['temp'])

                    # Replace NaN with ? to make error log clearer
                    df.loc[df.temp.isna(), 'temp'] = '?'

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default

                        expected_val = row['temp']
                        msg = f'Value {row[col]} in {col} not of data type {data_type}. (Expected: {expected_val})'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif data_type == 'DT':
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d').isna()

                    # TODO Does not identify date/time such as 'yyyy-mm-ddThh:mm:ssZ(+hh:mm)' as valid
                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not in the ISO date/time format or is an invalid date/time.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif data_type == 'U':
                    # Column can contain any numeric value
                    temp = pd.to_numeric(df[col], errors='coerce')
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & temp.isna()

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not of data type {data_type}. Numeric value expected.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif data_type == 'YN':
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].str.lower().str.match(r'^(yes|no|y|n)$')

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not of data type {data_type}.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif data_type == 'DMS':
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & ~df[col].str.match(r'^\d+:[0-5]\d:[0-5]\d.?\d*$')

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} not of data type {data_type} or is an invalid value.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                elif (data_type == 'ID') and col.startswith(group):
                    mask = df.HEADING.eq('DATA') & ~df[col].eq('') & df.duplicated(col, keep=False)

                    for row in df.loc[mask, :].to_dict('records'):
                        line_number = int(row['line_number'])
                        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                        # that Pandas returns by default
                        msg = f'Value {row[col]} in {col} is not unique.'
                        add_error_msg(ags_errors, 'AGS Format Rule 8', line_number, group, msg)

                # elif data_type == 'MC':
                #     # TODO Add check for MC
                #     pass

                # elif data_type == 'RL':
                #     # AGS Format Rule 11 should flag invalid RL entries
                #     pass

                # elif data_type in ['X', 'XN']:
                #     # Definition too broad to validate
                #     pass

        except IndexError:
            # No TYPE row in table
            pass

    return ags_errors


def rule_9(headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 9: GROUP and HEADING names will be taken from the standard AGS4 dictionary or
    defined in DICT table in the .ags file.
    '''

    for key in headings:
        # Extract list of headings defined for the group in the dictionaries
        mask = dictionary.DICT_GRP == key
        reference_headings_list = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        for item in [x for x in headings[key] if x not in ['HEADING', 'line_number']]:
            if item not in reference_headings_list:
                line_number = line_numbers[key]['HEADING']
                add_error_msg(ags_errors, 'AGS Format Rule 9', line_number, key, f'{item} not found in DICT table or the standard AGS4 dictionary.')

    return ags_errors


def rule_10a(tables, headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 10a: KEY fields in a GROUP must be present (even if null). There should not be any dupliate KEY field combinations.
    '''

    for group in tables:
        # Extract KEY fields from dictionary
        mask = (dictionary.DICT_GRP == group) & (dictionary.DICT_STAT.str.contains('key', case=False))
        key_fields = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        # Check for missing KEY fields
        for heading in key_fields:
            if heading not in headings[group]:
                line_number = line_numbers[group]['HEADING']
                add_error_msg(ags_errors, 'AGS Format Rule 10a', line_number, group, f'Key field {heading} not found.')

        # Check for duplicate KEY field combinations if all KEY fields are present
        if set(key_fields).issubset(set(headings[group])):
            # 'HEADING' column has to added explicity as it is not in the key field list
            key_fields = ['HEADING'] + key_fields

            mask = tables[group].duplicated(key_fields, keep=False)
            duplicate_rows = tables[group].loc[mask, :]

            for row in duplicate_rows.to_dict('records'):
                duplicate_key_combo = '|'.join([row[x] for x in row if x in key_fields])
                line_number = int(row['line_number'])
                # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                # that Pandas returns by default
                add_error_msg(ags_errors, 'AGS Format Rule 10a', line_number, group, f'Duplicate key field combination: {duplicate_key_combo}')

    return ags_errors


def rule_10b(tables, headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 10b: REQUIRED fields in a GROUP must be present and cannot be empty.
    '''

    for group in tables:
        # Extract REQUIRED fields from dictionary
        mask = (dictionary.DICT_GRP == group) & (dictionary.DICT_STAT.str.contains('required', case=False))
        required_fields = dictionary.loc[mask, 'DICT_HDNG'].tolist()

        # Check for missing REQUIRED fields
        for heading in required_fields:
            if heading not in headings[group]:
                line_number = line_numbers[group]['HEADING']
                add_error_msg(ags_errors, 'AGS Format Rule 10b', line_number, group, f'Required field {heading} not found.')

        # Check for missing entries in REQUIRED fields
        # First make copy of table so that it can be modified without unexpected side-effects
        df = tables[group].copy()

        for heading in set(required_fields).intersection(set(headings[group])):

            # Regex ^\s*$ should catch empty entries as well as entries that contain only whitespace
            mask = (df['HEADING'] == 'DATA') & df[heading].str.contains(r'^\s*$', regex=True)

            # Replace missing/blank entries with '???' so that they can be clearly seen in the output
            df[heading] = df[heading].str.replace(r'^\s*$', '???', regex=True)
            missing_required_fields = df.loc[mask, :]

            # Add each row with missing entries to the error log
            for row in missing_required_fields.to_dict('records'):
                msg = '|'.join([row[x] for x in row if x not in ['line_number']])
                line_number = int(row['line_number'])
                # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                # that Pandas returns by default
                add_error_msg(ags_errors, 'AGS Format Rule 10b', line_number, group, f'Empty REQUIRED fields: {msg}')

    return ags_errors


def rule_10c(tables, headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 10c: Each DATA row should have a parent entry in the parent GROUP.
    '''

    for group in tables:
        # Find parent group name
        # Groups without parents as per the Standard Dictionary are skipped
        if group not in ['PROJ', 'TRAN', 'ABBR', 'DICT', 'UNIT', 'TYPE', 'LOCA', 'FILE', 'LBSG', 'PREM', 'STND']:

            try:
                mask = (dictionary.DICT_TYPE == 'GROUP') & (dictionary.DICT_GRP == group)
                parent_group = dictionary.loc[mask, 'DICT_PGRP'].to_list()[0]

                # Check whether parent entries exist
                if parent_group == '':
                    add_error_msg(ags_errors, 'AGS Format Rule 10c', '-', group, 'Parent group left blank in dictionary.')

                else:
                    # Extract KEY fields from dictionary
                    mask = (dictionary.DICT_GRP == parent_group) & (dictionary.DICT_STAT.str.contains('key', case=False))
                    parent_key_fields = dictionary.loc[mask, 'DICT_HDNG'].tolist()
                    parent_df = tables[parent_group].copy()

                    mask = (dictionary.DICT_GRP == group) & (dictionary.DICT_STAT.str.contains('key', case=False))
                    child_key_fields = dictionary.loc[mask, 'DICT_HDNG'].tolist()
                    child_df = tables[group].copy()

                    # Return error message if parent group does not have any key fields
                    if not parent_key_fields:
                        msg = f'No key fields have been defined in parent group ({parent_group}). '\
                            'Please check DICT group.'
                        add_error_msg(ags_errors, 'AGS Format Rule 10c', '-', group, msg)

                    # Return error message if child group key fileds is not a superset of parent group key fields
                    elif not set(child_key_fields).issuperset(set(parent_key_fields)):
                        missing_key_fields = set(parent_key_fields).difference(set(child_key_fields))
                        msg = f'{", ".join(missing_key_fields)} defined as key field(s) in the parent group ({parent_group}) '\
                            'but not in the child group. Please check DICT group.'
                        add_error_msg(ags_errors, 'AGS Format Rule 10c', '-', group, msg)

                    else:
                        # Check that both child and parent groups have the parent key fields. Otherwise an IndexError will occur
                        # when merge operation is attempted
                        if set(parent_key_fields).issubset(set(headings[group])) and set(parent_key_fields).issubset(headings[parent_group]):
                            # Merge parent and child tables using parent key fields and find entries that not in the
                            # parent table
                            orphan_rows = child_df.merge(parent_df, how='left', on=parent_key_fields, indicator=True).query('''_merge=="left_only"''')

                            for row in orphan_rows.to_dict('records'):
                                msg = '|'.join([row[x] for x in row if x in parent_key_fields])
                                msg = f'Parent entry for line not found in {parent_group}: {msg}'
                                line_number = int(row['line_number_x'])  # 'line_number_x' because merge appends '_x' to column name in the left table
                                add_error_msg(ags_errors, 'AGS Format Rule 10c', line_number, group, msg)

                        else:
                            msg = f'Could not check parent entries due to missing key fields in {group} or {parent_group}. '\
                                'Check error log under AGS Format Rule 10a.'
                            line_number = line_numbers[group]['HEADING']
                            add_error_msg(ags_errors, 'AGS Format Rule 10c', line_number, group, msg)
                            # Missing key fields in child and/or parent groups. AGS Format Rule 10a should catch this error.

            except IndexError:
                msg = 'Could not check parent entries since group definitions not found in standard dictionary or DICT table.'
                add_error_msg(ags_errors, 'AGS Format Rule 10c', '-', group, msg)

            except KeyError:
                add_error_msg(ags_errors, 'AGS Format Rule 10c', '-', group, f'Could not find parent group {parent_group}.')

    return ags_errors


def rule_11(tables, headings, dictionary, ags_errors={}):
    '''AGS Format Rule 11: Data of TYPE "RL" shall be delimited by a single character defined under TRAN_DLIM.
    '''

    try:
        # Extract and check TRAN_DLIM and TRAN_RCON
        TRAN = tables['TRAN'].copy()

        delimiter = TRAN.loc[TRAN.HEADING == 'DATA', 'TRAN_DLIM'].values[0]
        concatenator = TRAN.loc[TRAN.HEADING == 'DATA', 'TRAN_RCON'].values[0]

        # Get line number
        line_number = int(TRAN.loc[TRAN.HEADING == 'DATA', 'line_number'].values[0])
        # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
        # that Pandas returns by default

        # Check AGS Format Rule 11a
        if delimiter == '':
            add_error_msg(ags_errors, 'AGS Format Rule 11a', line_number, 'TRAN', 'TRAN_DLIM missing.')

        # Check AGS Format Rule 11b
        if concatenator == '':
            add_error_msg(ags_errors, 'AGS Format Rule 11b', line_number, 'TRAN', 'TRAN_RCON missing.')

        # Check AGS Format Rule 11c (only if AGS Format Rule 11a and AGS Format Rule 11b are satisfied)
        if 'AGS Format Rule 11a' in ags_errors or 'AGS Format Rule 11b' in ags_errors:
            return ags_errors

        else:
            ags_errors = rule_11c(tables, dictionary, delimiter, concatenator, ags_errors=ags_errors)

    except KeyError:
        # TRAN group missing. AGS Format Rule 14 should catch this error.
        pass

    except IndexError:
        # TRAN group has no DATA rows. AGS Format Rule 14 should catch this error.
        pass

    return ags_errors


def rule_11c(tables, dictionary, delimiter, concatenator, ags_errors={}):
    '''AGS Format Rule 11c: Data type "RL" can cross-reference to any group in an AGS4 file
    '''

    # Check for columns of data type RL
    for group in tables:
        df = tables[group].copy()

        for col in df:
            if 'RL' in df.loc[df.HEADING == 'TYPE', col].tolist():
                # Filter out rows with blank RL entries
                rows_with_record_links = df.loc[df.HEADING.eq('DATA') & df[col].str.contains(r'.+', regex=True), :]

                for row in rows_with_record_links.to_dict('records'):
                    record_link = row[col]
                    line_number = int(row['line_number'])
                    # line_number is converted to int since the json module (particularly json.dumps) cannot process numpy.int64 data types
                    # that Pandas returns by default

                    # Return error message if delimiter is not found
                    if delimiter not in record_link:
                        msg = f'Invalid record link: "{record_link}". "{delimiter}" should be used as delimiter.'
                        add_error_msg(ags_errors, 'AGS Format Rule 11c', line_number, group, msg)
                        continue

                    # Convert record link to list and split using concatenator
                    record_link = record_link.split(concatenator)

                    # Check whether each link refers to a valid record
                    for item in record_link:
                        if fetch_record(item.split(delimiter), tables).shape[0] < 1:
                            msg = f'Invalid record link: "{item}". No such record found.'
                            add_error_msg(ags_errors, 'AGS Format Rule 11c', line_number, group, msg)

                        elif fetch_record(item.split(delimiter), tables).shape[0] > 1:
                            msg = f'Invalid record link: "{item}". Link refers to more than one record.'
                            add_error_msg(ags_errors, 'AGS Format Rule 11c', line_number, group, msg)

    return ags_errors


def rule_12(tables, headings, ags_errors={}):
    '''AGS Format Rule 12: Only REQUIRED fields needs to be filled. Others can be null.
    '''

    # This is already checked by AGS Format Rule 10b. No additional checking necessary

    return ags_errors


def rule_13(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 13: File shall contain a PROJ group with only one DATA row. All REQUIRED fields in this
    row should be filled.
    '''

    if 'PROJ' not in tables.keys():
        add_error_msg(ags_errors, 'AGS Format Rule 13', '-', 'PROJ', 'PROJ table not found.')

    elif tables['PROJ'].loc[tables['PROJ']['HEADING'] == 'DATA', :].shape[0] < 1:
        line_number = line_numbers['PROJ']['GROUP']
        add_error_msg(ags_errors, 'AGS Format Rule 13', line_number, 'PROJ', 'There should be at least one DATA row in the PROJ table.')

    elif tables['PROJ'].loc[tables['PROJ']['HEADING'] == 'DATA', :].shape[0] > 1:

        # Return an error for all DATA rows after the first one
        for line_number in tables['PROJ'].loc[tables['PROJ']['HEADING'] == 'DATA', 'line_number'].tolist()[1:]:
            add_error_msg(ags_errors, 'AGS Format Rule 13', line_number, 'PROJ', 'There should not be more than one DATA row in the PROJ table.')

    return ags_errors


def rule_14(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 14: File shall contain a TRAN group with only one DATA row. All REQUIRED fields in this
    row should be filled.
    '''

    if 'TRAN' not in tables.keys():
        add_error_msg(ags_errors, 'AGS Format Rule 14', '-', 'TRAN', 'TRAN table not found.')

    elif tables['TRAN'].loc[tables['TRAN']['HEADING'] == 'DATA', :].shape[0] < 1:
        line_number = line_numbers['TRAN']['GROUP']
        add_error_msg(ags_errors, 'AGS Format Rule 14', line_number, 'TRAN', 'There should be at least one DATA row in the TRAN table.')

    elif tables['TRAN'].loc[tables['TRAN']['HEADING'] == 'DATA', :].shape[0] > 1:

        # Return an error for all DATA rows after the first one
        for line_number in tables['TRAN'].loc[tables['TRAN']['HEADING'] == 'DATA', 'line_number'].tolist()[1:]:
            add_error_msg(ags_errors, 'AGS Format Rule 14', line_number, 'TRAN', 'There should not be more than one DATA row in the TRAN table.')

    return ags_errors


def rule_15(tables, headings, line_numbers, ags_errors={}):
    '''AGS Format Rule 15: The UNIT group shall list all units used in within the data file.
    '''

    try:
        # Load UNIT group
        UNIT = tables['UNIT'].copy()

        unit_list = []

        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy().filter(regex=r'[^line_number]')

            unit_list += df.loc[df['HEADING'] == 'UNIT', :].values.flatten().tolist()

        try:
            # Check whether entries in the type_list are defined in the UNIT table
            for entry in set(unit_list):
                if entry not in UNIT.loc[UNIT['HEADING'] == 'DATA', 'UNIT_UNIT'].to_list() and entry not in ['', 'UNIT']:
                    # Returns the line number of the UNIT group, not the line number of the missing unit
                    line_number = line_numbers['UNIT']['GROUP']
                    add_error_msg(ags_errors, 'AGS Format Rule 15', line_number, 'UNIT', f'Unit "{entry}" not found in UNIT table.')

        except KeyError:
            # TYPE_TYPE column missing. AGS Format Rule 10a and 10b should catch this error
            pass

    except KeyError:
        add_error_msg(ags_errors, 'AGS Format Rule 15', '-', 'UNIT', 'UNIT table not found.')

    return ags_errors


def rule_16(tables, headings, dictionary, ags_errors={}):
    '''AGS Format Rule 16: Data file shall contain an ABBR group with definitions for all abbreviations used in the file.
    '''

    try:
        # Load ABBR group
        ABBR = tables['ABBR'].copy()

        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy()

            for heading in headings[group]:
                # Check whether column is of data type PA
                if 'PA' in df.loc[df['HEADING'] == 'TYPE', heading].tolist():
                    # Convert entries in column to a set to drop duplicates
                    entries = set(df.loc[df['HEADING'] == 'DATA', heading].to_list())

                    try:
                        # Extract concatenated entries (if they exist) using TRAN_RCON (if it exists)
                        concatenator = tables['TRAN'].loc[tables['TRAN']['HEADING'] == 'DATA', 'TRAN_RCON'].values[0]
                        entries = [entry.split(concatenator) for entry in entries]

                        # The split operation will result in a list of lists that has to be flattened
                        entries = [item for sublist in entries for item in sublist]

                    except KeyError:
                        # KeyError will be raised if TRAN or TRAN_RCON does not exist. AGS Format Rule 14 will catch this error.
                        pass

                    except IndexError:
                        # IndexError will be raised if no DATA rows in ABBR table. AGS Format Rule 14 will catch this error.
                        pass

                    except ValueError:
                        # ValueError will be raised by entry.split(concatenator) if TRAN_RCON is empty.
                        # This error should be caught by AGS Format Rule 11b.
                        pass

                    try:
                        # Check whether entries in the column is defined in the ABBR table
                        for entry in entries:
                            if entry not in ABBR.loc[ABBR['ABBR_HDNG'] == heading, 'ABBR_CODE'].to_list() and entry not in ['']:
                                msg = f'"{entry}" under {heading} in {group} not found in ABBR table.'
                                add_error_msg(ags_errors, 'AGS Format Rule 16', '-', group, msg)

                    except KeyError:
                        # ABBR_HDNG and/or ABBR_CODE column missing. AGS Format Rule 10a and 10b should catch this error.
                        pass

    except KeyError:
        # ABBR table is not required if no columns of data type PA are found
        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy()

            for heading in headings[group]:
                # Check whether column is of data type PA
                if 'PA' in df.loc[df['HEADING'] == 'TYPE', heading].tolist():
                    add_error_msg(ags_errors, 'AGS Format Rule 16', '-', 'ABBR', 'ABBR table not found.')

                    # Break out of function as soon as first column of data type PA is found to
                    # avoid duplicate error entries
                    return ags_errors

    return ags_errors


def rule_17(tables, headings, dictionary, ags_errors={}):
    '''AGS Format Rule 17: Data file shall contain a TYPE group with definitions for all data types used in the file.
    '''

    try:
        # Load TYPE group
        TYPE = tables['TYPE'].copy()

        type_list = []

        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy().filter(regex=r'[^line_number]')

            type_list += df.loc[tables[group]['HEADING'] == 'TYPE', :].values.flatten().tolist()

        try:
            # Check whether entries in the type_list are defined in the TYPE table
            for entry in set(type_list):
                if entry not in TYPE.loc[TYPE['HEADING'] == 'DATA', 'TYPE_TYPE'].to_list() and entry not in ['TYPE']:
                    add_error_msg(ags_errors, 'AGS Format Rule 17', '-', 'TYPE', f'Data type "{entry}" not found in TYPE table.')

        except KeyError:
            # TYPE_TYPE column missing. AGS Format Rule 10a and 10b should catch this error
            pass

    except KeyError:
        add_error_msg(ags_errors, 'AGS Format Rule 17', '-', 'TYPE', 'TYPE table not found.')

    return ags_errors


def rule_18(tables, headings, ags_errors={}):
    '''AGS Format Rule 18: Data file shall contain a DICT group with definitions for all non-standard headings in the file.

    Note: Check is based on rule_9(). The 'ags_errors' input should be the output from rule_9() in order for this to work.
    '''

    if 'DICT' not in tables.keys() and 'AGS Format Rule 9' in ags_errors.keys():
        # If AGS Format Rule 9 has been violated that means a non-standard has been found
        msg = 'DICT table not found. '\
              'See error log under AGS Format Rule 9 for a list of non-standard headings that need to be defined in a DICT table.'
        add_error_msg(ags_errors, 'AGS Format Rule 18', '-', 'DICT', f'{msg}')

    return ags_errors


def rule_19b_2(tables, headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 19b: HEADING names shall start with the group name followed by an underscore character.
    Where a HEADING refers to an existing HEADING within another GROUP, it shall bear the same name.
    '''

    for group in tables:

        # Check heading names in current table not including 'HEADING' and 'line_number'
        for heading in [x for x in headings[group] if x not in ['HEADING', 'line_number']]:
            ref_group_name = heading.split('_')[0]

            # The standard dictionaries allow fields like 'SPEC_REF' and 'TEST_STAT' which break AGS Format Rule 19b
            # so headings starting with 'SPEC' and 'TEST' are considered exceptions to the rule
            if ref_group_name not in [group, 'SPEC', 'TEST']:
                ref_headings_list_1 = dictionary.loc[dictionary.HEADING.eq('DATA') & dictionary.DICT_GRP.eq(ref_group_name), 'DICT_HDNG'].tolist()
                ref_headings_list_2 = dictionary.loc[dictionary.HEADING.eq('DATA') & dictionary.DICT_GRP.eq(group), 'DICT_HDNG'].tolist()

                if not ref_headings_list_1:
                    msg = f'Group {ref_group_name} referred to in {heading} could not be found in either the standard dictionary or the DICT table.'
                    line_number = line_numbers[group]['HEADING']
                    add_error_msg(ags_errors, 'AGS Format Rule 19b', line_number, group, msg)

                elif heading not in ref_headings_list_1 and heading in ref_headings_list_2:
                    msg = f'Definition for {heading} not found under group {ref_group_name}. '\
                           'Either rename heading or add definition under correct group.'
                    line_number = line_numbers[group]['HEADING']
                    add_error_msg(ags_errors, 'AGS Format Rule 19b', line_number, group, msg)

                else:
                    # Heading is not defined at all. This will be caught by AGS Format Rule 9
                    pass

    return ags_errors


def rule_19b_3(tables, headings, dictionary, line_numbers, ags_errors={}):
    '''AGS Format Rule 19b: HEADING names shall start with the group name followed by an underscore character.
    Where a HEADING refers to an existing HEADING within another GROUP, it shall bear the same name.
    '''

    for group in tables:

        # Check heading names in current table not including 'HEADING' and 'line_number'
        for heading in [x for x in headings[group] if x not in ['HEADING', 'line_number']]:

            try:
                ref_group_name = heading.split('_')[0]

                if (ref_group_name != group) and heading not in dictionary.DICT_HDNG.to_list():
                    msg = f'{heading} does not start with the name of this group, nor is it defined in another group.'
                    line_number = line_numbers[group]['HEADING']
                    add_error_msg(ags_errors, 'AGS Format Rule 19b', line_number, group, msg)

            except IndexError:
                # Heading does not have an underscore in it. AGS Format Rule 19b should catch this error.
                pass

    return ags_errors


def rule_20(tables, headings, filepath, ags_errors={}):
    '''AGS Format Rule 20: Additional computer files included within a data submission shall be defined in a FILE GROUP.
    '''

    import os

    try:
        # Load FILE group
        FILE = tables['FILE'].copy()

        # Check whether all FILE_FSET entries in the file are defined in the FILE group
        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy()

            if 'FILE_FSET' in headings[group]:
                file_list = df.loc[(df.HEADING == 'DATA') & df.FILE_FSET.str.contains(r'[a-zA-Z0-9]', regex=True), 'FILE_FSET'].tolist()

                for entry in set(file_list):
                    if entry not in FILE.loc[FILE.HEADING == 'DATA', 'FILE_FSET'].tolist():
                        # Return line numbers where missing entry appears
                        line_numbers = df.loc[df['FILE_FSET'] == entry, 'line_number'].tolist()

                        for line_number in line_numbers:
                            msg = f'FILE_FSET entry "{entry}" not found in FILE table.'
                            add_error_msg(ags_errors, 'AGS Format Rule 20', line_number, group, msg)

        # Verify that a sub-directory named "FILE" exists in the same directory as the AGS4 file being checked
        current_dir = os.path.dirname(filepath)

        if not os.path.isdir(os.path.join(current_dir, 'FILE')):
            msg = 'Folder named "FILE" not found. Files defined in the FILE table should be saved in this folder.'
            add_error_msg(ags_errors, 'AGS Format Rule 20', '-', 'FILE', msg)

        # Verify entries in FILE group
        for file_fset in set(FILE.loc[FILE.HEADING == 'DATA', 'FILE_FSET'].tolist()):
            file_fset_path = os.path.join(current_dir, 'FILE', file_fset)

            if not os.path.isdir(file_fset_path):
                msg = f'Sub-folder named "{os.path.join("FILE", file_fset)}" not found even though it is defined in the FILE table.'
                add_error_msg(ags_errors, 'AGS Format Rule 20', '-', 'FILE', msg)

            else:
                # If sub-directory exists, then continue to check files
                for file_name in set(FILE.loc[FILE.FILE_FSET == file_fset, 'FILE_NAME'].tolist()):
                    file_name_path = os.path.join(current_dir, 'FILE', file_fset, file_name)

                    if not os.path.isfile(file_name_path):
                        msg = f'File named "{os.path.join("FILE", file_fset, file_name)}" not found even though it is defined in the FILE table.'

                        # Return line numbers where missing entry appears
                        line_numbers = FILE.loc[FILE['FILE_NAME'] == file_name, 'line_number'].tolist()

                        for line_number in line_numbers:
                            add_error_msg(ags_errors, 'AGS Format Rule 20', line_number, 'FILE', msg)

    except KeyError:
        # FILE group not found. It is only required if FILE_FSET entries are found in other groups

        for group in tables:
            # First make copy of group to avoid potential changes and side-effects
            df = tables[group].copy()

            if 'FILE_FSET' in headings[group]:
                file_list = df.loc[(df.HEADING == 'DATA') & df.FILE_FSET.str.contains(r'[a-zA-Z0-9]', regex=True), 'FILE_FSET'].tolist()

                if len(file_list) > 0:
                    msg = 'FILE table not found even though there are FILE_FSET entries in other tables.'
                    add_error_msg(ags_errors, 'AGS Format Rule 20', '-', 'FILE', msg)

                    # Break out of function as soon as a group with a FILE_FSET entry is found to
                    # avoid duplicate error entries
                    return ags_errors

    return ags_errors


def is_ags3(tables, input_file, ags_errors={}):
    '''Check if file is likely to be in AGS3 format and issue warning.
    '''

    import re

    # Check whether dictionary of tables is empty
    if not tables:

        # If True, then check for AGS3 like entries
        with open(input_file, mode='r') as f:
            lines = f.read()

            if re.findall(r'"\*\*[a-zA-Z0-9]+"', lines):
                msg = 'No AGS4 tables found but lines starting with "**" detected. '\
                      'Therefore, it is possible that this file is in AGS3 format instead of AGS4.'
                add_error_msg(ags_errors, 'General', '', '', msg)

                msg = 'Checking AGS3 files is not supported. The errors listed below are valid only if this file is confirmed to be an AGS4 file.'
                add_error_msg(ags_errors, 'General', '', '', msg)

    return ags_errors


def is_ags3_like(line, line_number=0, ags_errors={}):
    '''Check if file is likely to be in AGS3 format and issue warning.
    '''

    if line.startswith(r'"**PROJ"'):
        msg = 'Line starts with "**PROJ" instead of a valid data descriptor. This indicates that file is in the AGS3 format which is not supported.'
        add_error_msg(ags_errors, 'AGS Format Rule 3', line_number, '', msg)

    return ags_errors
