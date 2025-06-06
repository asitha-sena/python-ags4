# Copyright (C) 2020-2025  Asitha Senanayake
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

import logging

logger = logging.getLogger(__name__)


# Read functions #

def AGS4_to_dict(filepath_or_buffer, encoding='utf-8', get_line_numbers=False, rename_duplicate_headers=True):
    """Load all the data in an AGS4 file to a dictionary of dictionaries.

    Each GROUP in the AGS4 file is assigned its own dictionary.

    'AGS4_to_dataframe()' function uses this function to load AGS4 data in to
    Pandas dataframes.

    Parameters
    ----------
    filepath_or_buffer : File path (str, pathlib.Path), or StringIO.
        Path to AGS4 file or any object with a read() method (such as an open
        file or StringIO).
    encoding : str, default='utf-8'
        Encoding of text file. This can be set to 'utf-8-sig' to read files that
        begin with a byte-order-mark.
    get_line_numbers : bool, default=False
        Add line number column to each table (for UNIT, TYPE, and DATA rows) and
        return a dictionary with line numbers for GROUP and HEADING lines.
    rename_duplicate_headers: bool, default=True
        Rename duplicate headers if found. Neither AGS4 tables nor Pandas
        dataframes allow duplicate headers, therefore a number will be appended
        to duplicates to make them unique.

    Returns
    -------
    data : dict of dicts
        Dictionary populated with data from the AGS4 file with AGS4 headers as
        keys.
    headings : dict of lists
        Dictionary with the headings in the each GROUP (This will be needed to
        recall the correct column order when writing Pandas dataframes back to
        AGS4 files. i.e. input for 'dataframe_to_AGS4()' function)
    line_numbers : dict of int, only if get_line_numbers=True
        Dictionary with the starting line numbers of GROUP and HEADING rows.
        This is only required for checking a .ags file with 'check_file()'
        function.
    """

    if _is_file_like(filepath_or_buffer):
        f = filepath_or_buffer
        f.seek(0)
        if hasattr(f, 'encoding') and getattr(f, 'encoding', None) != encoding and hasattr(f, 'reconfigure'):
            f.reconfigure(encoding=encoding)
        close_file = False
    else:
        # Read file with errors="replace" to catch UnicodeDecodeErrors
        f = open(filepath_or_buffer, "r", encoding=encoding, errors="replace")
        close_file = True

    try:

        data = {}
        headings = {}
        line_numbers = {}

        # NOTE: The 'headings' dict is not really necessary for the read AGS4
        # function but will be needed to write the columns of Pandas dataframes
        # when writing them back to AGS4 files. (The HEADING column needs to be
        # the first column in order to preserve the AGS data format. Other
        # columns in certain groups have a preferred order as well)

        for i, line in enumerate(f, start=1):
            if _is_bytebuffer(line):
                line = line.decode(encoding)

            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            if temp[0] == 'GROUP':
                group = temp[1]

                # Raise exception if duplicate group is found as previous copy
                # of that group will be overwritten
                if group in data.keys():
                    msg = f"{group} group duplicated in Line {i}. Cannot parse file without overwriting data, "\
                           "therefore please combine all duplicate groups first."

                    logger.error(msg)
                    raise AGS4Error(msg)

                else:
                    data[group] = {}

                # Store GROUP line number (A default 'HEADING' entry is added to
                # avoid KeyErrors in case of missing HEADING rows)
                line_numbers[group] = {'GROUP': i, 'HEADING': '-'}

            elif temp[0] == 'HEADING':

                # Catch HEADER rows with duplicate entries as it will result in
                # a dictionary with arrays of unequal lengths and cause a
                # ValueError when trying to convert to a Pandas dataframe
                if len(temp) != len(set(temp)):

                    if rename_duplicate_headers is False:
                        raise AGS4Error(f"HEADER row in {group} (Line {i}) has duplicate entries")

                    logger.warning(f"HEADER row in {group} (Line {i}) has duplicate entries.")

                    # Rename duplicate headers by appending a number
                    item_count = {}

                    for i, item in enumerate(temp):
                        if item not in item_count:
                            item_count[item] = {'i': i, 'count': 0}
                        else:
                            item_count[item]['i'] = i
                            item_count[item]['count'] += 1
                            count = item_count[item]['count']

                            temp[i] = temp[i]+'_'+str(item_count[item]['count'])

                            logger.info(f'Duplicate column {item} found and renamed as {item}_{count}. '
                                        'Automatically renamed columns do not conform to AGS4 Rules 19a and 19b. '
                                        'Therefore, please review the data and rename or drop duplicate columns as appropriate.')

                # Store HEADING line number
                line_numbers[group]['HEADING'] = i

                # Store UNIT, TYPE, and DATA line numbers
                if get_line_numbers is True:
                    temp.append('line_number')

                headings[group] = temp

                for item in temp:
                    data[group][item] = []

            elif temp[0] in ['TYPE', 'UNIT', 'DATA']:

                # Append line number
                if get_line_numbers is True:
                    temp.append(i)

                # Check whether line has the same number of entries as the
                # number of headings in the group. If not, print error and exit.
                if len(temp) != len(headings[group]):
                    logger.error(f"Line {i} does not have the same number of entries as the HEADING row in {group}.")
                    raise AGS4Error(f"Line {i} does not have the same number of entries as the HEADING row in {group}.")

                for i in range(0, len(temp)):
                    data[group][headings[group][i]].append(temp[i])

            else:
                continue
    finally:
        if close_file:
            f.close()

    if get_line_numbers is True:
        return data, headings, line_numbers

    return data, headings


def AGS4_to_dataframe(filepath_or_buffer, encoding='utf-8', get_line_numbers=False, rename_duplicate_headers=True):
    """Load all the tables in an AGS4 file to a dictionary of Pandas dataframes.

    The output is a dictionary of dataframes with the name of each AGS4 table
    (i.e. GROUP) as the primary key.

    Parameters
    ----------
    filepath_or_buffer : str, StringIO
        Path to AGS4 file or any file like object (open file or StringIO).
    encoding : str, default='utf-8'
        Encoding of text file. This can be set to 'utf-8-sig' to read files that
        begin with a byte-order-mark.
    get_line_numbers : bool, default=False
        Add line number column to each table (for UNIT, TYPE, and DATA rows) and
        return a dictionary with line numbers for GROUP and HEADING lines.
    rename_duplicate_headers: bool, default=True
        Rename duplicate headers if found. Neither AGS4 tables nor Pandas
        dataframes allow duplicate headers, therefore a number will be appended
        to duplicates to make them unique.

    Returns
    -------
    tables : dict of dataframes
        Dictionary populated with Pandas dataframes. Each GROUP in the AGS4
        files is assigned to its a dataframe.
    headings : dict of lists
        Dictionary with the headings in the each GROUP (This will be needed to
        recall the correct column order when writing Pandas dataframes back to
        AGS4 files. i.e. input for 'dataframe_to_AGS4()' function)
    line_numbers : dict of int, only if get_line_numbers=True
        Dictionary with the starting line numbers of GROUP and HEADING rows.
        This is only required for checking a .ags file with 'check_file()'
        function.

    """

    from pandas import DataFrame

    # Extract AGS4 file into a dictionary of dictionaries. A dictionary with
    # group line numbers is returned, in addition to data and headings, for
    # checking purposes.
    if get_line_numbers is True:
        data, headings, line_numbers = AGS4_to_dict(filepath_or_buffer, encoding=encoding, get_line_numbers=get_line_numbers,
                                                    rename_duplicate_headers=rename_duplicate_headers)

        # Convert dictionary of dictionaries to a dictionary of Pandas
        # dataframes
        tables = {}
        for key in data:
            tables[key] = DataFrame(data[key])

        return tables, headings, line_numbers

    # Otherwise only the data and the headings are returned
    data, headings = AGS4_to_dict(filepath_or_buffer, encoding=encoding,
                                  rename_duplicate_headers=rename_duplicate_headers)

    # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
    tables = {}
    for key in data:
        tables[key] = DataFrame(data[key])

    return tables, headings


def AGS4_to_excel(input_file, output_file, encoding='utf-8', rename_duplicate_headers=True, sorting_strategy=None):
    """Load all the tables in an AGS4 file to an Excel spreasheet.

    Parameters
    ----------
    input_file : str
        Path to AGS4 file
    output_file : str
        Path to Excel file
    encoding : str, default='utf-8'
        Encoding of text file. This can be set to 'utf-8-sig' to read files that
        begin with a byte-order-mark.
    rename_duplicate_headers: bool, default=True
        Rename duplicate headers if found. Neither AGS4 tables nor Pandas
        dataframes allow duplicate headers, therefore a number will be appended
        to duplicates to make them unique.
    sorting_strategy : {None, 'dictionary', 'alphabetical', 'hierarchical'}, default=None
        Sort groups in the order in which they appear in the dictionary, the
        hierarchy defined in the dictionary, or alphabetically.
        WARNING: The original order of groups will be lost and cannot be
        restored when .xlsx file is converted back to .ags.

    Returns
    -------
    None
    """

    from pandas import ExcelWriter
    from openpyxl.utils import get_column_letter

    # Extract AGS4 file into a dictionary of dictionaries
    tables, headings = AGS4_to_dataframe(input_file, encoding=encoding,
                                         rename_duplicate_headers=rename_duplicate_headers)

    # Create list of tables that can be sorted
    if sorting_strategy is not None:
        sorting_desc = {'dictionary': 'according to the order of appearance in the dictionary',
                        'alphabetical': 'alphabetically',
                        'hierarchical': 'according to the hierarchy defined in the dictionary'}
        msg = f'WARNING: Worksheets in Excel file will be sorted {sorting_desc[sorting_strategy]}. The original group order will be lost.'
        logger.warning(f"{msg}")

        list_of_tables = sort_groups(tables, sorting_strategy=sorting_strategy)

    else:
        list_of_tables = tables.keys()

    # Exit if there is no AGS4 tables in the input file
    if len(list_of_tables) == 0:
        logger.error('No valid AGS4 data found in input file.')
        raise AGS4Error('No valid AGS4 data found in input file.')

    # Write to Excel file
    with ExcelWriter(output_file, engine='openpyxl') as writer:
        for key in list_of_tables:
            logger.info(f'Writing data from... {key}')

            # Check table size and issue warning for large files that could crash the program
            if 25000 < tables[key].shape[0] < 100000:
                logger.info(f'{key} has {tables[key].shape[0]} rows, so it will take about a minute to export.')
            elif tables[key].shape[0] > 100000:
                logger.warning(f'{key} has {tables[key].shape[0]} rows, so it may take a few minutes to export. '
                               'The program will terminate if it runs out of memory in the process.')

            tables[key].to_excel(writer, sheet_name=key, index=False)

            # Update column widths in xlxs file to fit contents
            for i, col in enumerate(tables[key], start=1):
                # 13 < colummn_width < 75 characters (approximately)
                max_width = min(max(13, tables[key][col].map(len).max() + 1), 75)

                writer.sheets[key].column_dimensions[get_column_letter(i)].width = max_width


# Write functions #

def dataframe_to_AGS4(tables, headings, filepath, mode='w', index=False, encoding='utf-8', warnings=True):
    """Write a dictionary of Pandas dataframes that have been extracted using
    'AGS4_to_dataframe()' function back to an AGS4 file.

    Parameters
    ----------
    tables : dict of dataframes
        Dictionary of Pandas dataframes (output from 'AGS4_to_dataframe()')
    headings : dict of lists
        Dictionary of lists containing AGS4 headings in the correct order (e.g.
        output from 'AGS4_to_dataframe()'). Columns can be dropped and/or
        reordered using this option. An empty dictionary {} should be passed to
        export data without explicitly defining the column order.
    filepath : str
        Path to output file
    mode : {'w', 'a'}
        Option to write ('w') or append ('a') data.
    index : bool, default=False
        Include the index column when writing to file. WARNING: The output will
        not be a valid AGS4 file if set to True.
    encoding : str, default='utf-8'
        Encoding of output file
    warnings : bool, default=False
        Print warnings

    Returns
    -------
    None
    """

    # Open file and write/append data
    with open(filepath, mode, newline='', encoding=encoding) as f:
        for key in tables:
            # First make copy of table to avoid unexpected side-effects
            df = tables[key].copy()

            # Take care of an edge case where quoted text is present in a field.
            # The to_csv function automatically adds an extra pair of quotes
            # around any quoted strings that is encountered and there is no way
            # work around it as of Pandas v1.1.5. Therefore, double-double
            # quotes required by AGS4 Rule 5 are changed to single-double quotes
            # before the to_csv function is called. This ensures that the output
            # file has the quoted string in double-double quotes.
            for col in df.select_dtypes(include='object'):
                # Loop through columns that contain strings, find entries with '""', and replace
                # them with '""
                mask = df[col].str.contains('""', na=False)
                df.loc[mask, :] = df.loc[mask, :].apply(lambda x: x.str.replace('""', '"'))

            # Write table to file
            logger.info(f'Writing data from... {key}')
            f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')

            if key not in headings:
                logger.warning(f"Input 'headings' dictionary does not have an entry named {key}. "
                               f"All columns in the {key} table will be exported in the default order. "
                               "Please check column order and ensure AGS4 Rule 7 is still satisfied.")

                df.to_csv(f, index=index, quoting=1, lineterminator='\r\n', encoding=encoding)
                f.write("\r\n")

            elif set(headings[key]).difference(set(df.columns)):
                # Take care of another edge case where all column names defined
                # in the headings list may not be in the corresponding table due
                # to modifications by the user. Therefore, use a modified
                # headings list to export the remaining columns in the specified
                # order.
                # https://gitlab.com/ags-data-format-wg/ags-python-library/-/issues/69

                missing_cols = set(headings[key]).difference(set(df.columns))
                columns = [x for x in headings[key] if x not in missing_cols]

                logger.warning(f"Columns {', '.join(missing_cols)} not found in the {key} table although they are in the headings dictionary.")

                df.to_csv(f, index=index, quoting=1, columns=columns, lineterminator='\r\n', encoding=encoding)
                f.write("\r\n")

            else:
                columns = headings[key]

                df.to_csv(f, index=index, quoting=1, columns=columns, lineterminator='\r\n', encoding=encoding)
                f.write("\r\n")


def excel_to_AGS4(input_file, output_file, format_numeric_columns=True, dictionary=None):
    """Export AGS4 data in Excel file to an AGS4 file.

    Parameters
    ----------
    input_file : str
        Path to Excel file (Note: Each GROUP should be in a separate worksheet.
        e.g. output from AGS4.AGS4_to_excel)
    output_file : str
        Path to AGS4 file
    format_numeric_columns : bool, default=True
        Format numeric columns to match specified TYPE
    dictionary : str, optional
        Filepath to dictionary if the UNIT and TYPE data in tables need to be
        overridden.

    Returns
    -------
    None
    """

    from pandas import read_excel

    # Read data from Excel file in to a dictionary of dataframes
    tables = read_excel(input_file, sheet_name=None, engine='openpyxl',
                        keep_default_na=False, na_values='')

    # Not all worksheets in the spreadsheet may contain valid AGS4 tables, therefore
    # initiate variable to keep track of worksheets to export
    valid_tables = []

    for key, df in tables.items():
        # Assume that only worksheets with a 'HEADING' column contain valid AGS4 data
        if 'HEADING' in df:
            valid_tables.append(key)
        else:
            logger.warning(f'Worksheet {key} dropped as it does not have a HEADING column.')
            continue

        # List column names that don't conform to Rule 19 (using a negative look-ahead regex)
        for col_name in df.filter(regex=r'^(?!HEADING|^[A-Z0-9]{4}_[A-Z0-9]{1,4}$)', axis='columns'):
            logger.warning(f'Column {col_name} dropped as name does not conform to AGS4 Rule 19.')

        # Drop columns that don't conform to Rule 19
        df = df.filter(regex=r'HEADING|^[A-Z0-9]{4}_[A-Z0-9]{1,4}$', axis='columns')

        # Drop rows that are not 'UNIT', 'TYPE', or 'DATA'
        df = df.loc[df.HEADING.isin(['UNIT', 'TYPE', 'DATA']), :]

        # Finally format numeric column if required
        if format_numeric_columns is True:
            logger.info(f'Formatting columns in... {key}')
            tables[key] = convert_to_text(df, dictionary=dictionary)

    # Export dictionary of DataFrames to AGS4 file
    if len(valid_tables) == 0:
        logger.warning('No valid AGS4 data found in input file. Please see warning messages above.')
    else:
        dataframe_to_AGS4({key: tables[key] for key in valid_tables}, {}, output_file, warnings=False)


# Formatting functions #

def convert_to_numeric(dataframe):
    """The AGS4_to_dataframe() function extracts the data from an AGS4 file and
    puts each table into a Pandas DataFrame as text. This function reads the
    TYPE row and coverts the columns with data types DP, SF, SCI, and MC into
    numerical data. This allows the data to be plotted and used in
    calculations/formulas.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Pandas DataFrame from 'AGS4.AGS4_to_dataframe()' function

    Returns
    -------
    Pandas DataFrame
        Dataframe with numerical columns converted from text to numeric
        datatypes, the TYPE and UNIT rows (i.e. rows 1 and 2) removed, and the
        index reset.
    """

    from pandas import to_numeric

    # First create a copy of the DataFrame to avoid overwriting the
    # original data
    df = dataframe.copy()

    # Convert appropriate columns to numeric
    numeric_df = df.loc[:, df.iloc[1].str.contains('DP|MC|SF|SCI', na=False)].apply(to_numeric, errors='coerce')

    # Replace columns in input dataframe with numeric columns
    df[numeric_df.columns] = numeric_df

    # Remove TYPE and UNIT rows and reset index
    df = df.iloc[2:, :].reset_index(drop=True)

    return df


def convert_to_text(dataframe, dictionary=None):
    """Convert AGS4 DataFrame with numeric columns back to formatted text.

    This is necessary when exporting a dataframe back to an AGS4 file since
    columns of datatype 'float' may not get exported with the correct number of
    decimal places. If UNIT and TYPE rows are missing from the input dataframe,
    then they can be added by providing a AGS4 dictionary with that information.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Pandas DataFrame with numeric columns. e.g. output from
        'AGS4.convert_to_numeric()' function
    dictionary : str, optional
        Path to AGS4 dictionary file from which to get UNIT and TYPE rows and to
        convert to numeric fields to required precision. The values from the
        dictionary will override those already in the UNIT and TYPE rows in the
        dataframe. A standard dictionary can be picked using the one of the
        following strings '4.1.1', '4.1', '4.0.4', '4.0.3', '4.0'.

    Returns
    -------
    Pandas DataFrame
        A Pandas DataFrame with numeric columns converted to text and formatted
        to the correct precision. UNIT and TYPE rows will be added if that
        information is provided as an input.
    """

    from python_ags4 import check

    # Make copy of dataframe and reset index to make sure numbering
    # starts from zero
    df = dataframe.copy().reset_index(drop=True)

    # Check whether to use UNIT and TYPE rows in dataframe or to
    # retrieve values from the dictionary file
    if dictionary is None:
        # Check whether dataframe has "UNIT" and "TYPE" rows
        if ('UNIT' in df.HEADING.values) and ('TYPE' in df.HEADING.values):

            for col in df.columns:
                TYPE = df.loc[df.HEADING == 'TYPE', col].values[0]
                df = format_numeric_column(df, col, TYPE)

        else:
            logger.error('Cannot convert to text as UNIT and/or TYPE row(s) are missing. '
                         'Please provide dictonary file or add UNIT & TYPE rows to input file to proceed.')
            raise AGS4Error("Cannot convert to text as UNIT and/or TYPE row(s) are missing. "
                            "Please provide dictonary file or add UNIT & TYPE rows to input file to proceed.")

    else:
        # Read dictionary file
        if dictionary in ['4.1.1', '4.1', '4.0.4', '4.0.3', '4.0']:
            # Filepath to the standard dictionary will be picked based on version
            # number if a valid version number is provided. If it is not specified
            # at all, then the filepath will be selected based on the value of
            # TRAN_AGS in the TRAN table.
            dictionary = check.pick_standard_dictionary(dict_version=dictionary)

        temp, _ = AGS4_to_dataframe(dictionary)
        DICT = temp['DICT']

        # Check whether UNIT and TYPE rows are already in dataframe
        is_UNIT_row_present = 'UNIT' in df.HEADING.values
        is_TYPE_row_present = 'TYPE' in df.HEADING.values

        # Format columns and add UNIT/TYPE rows if necessary
        for col in df.columns:

            if col == 'HEADING':

                if not is_UNIT_row_present:
                    df.loc[-2, 'HEADING'] = 'UNIT'

                if not is_TYPE_row_present:
                    df.loc[-1, 'HEADING'] = 'TYPE'

            else:

                try:
                    # Get type and unit from dictionary
                    TYPE = DICT.loc[DICT.DICT_HDNG == col, 'DICT_DTYP'].iloc[0]
                    UNIT = DICT.loc[DICT.DICT_HDNG == col, 'DICT_UNIT'].iloc[0]

                    if is_UNIT_row_present:
                        # Overwrite existing UNIT with one from the dictionary
                        df.loc[df.HEADING == 'UNIT', col] = UNIT
                    else:
                        # Add UNIT row if one is not already there
                        df.loc[-2, col] = UNIT

                    if is_TYPE_row_present:
                        # Overwrite existing TYPE with one from the dictionary
                        df.loc[df.HEADING == 'TYPE', col] = TYPE
                    else:
                        # Add TYPE row if one is not already there
                        df.loc[-1, col] = TYPE

                    df = format_numeric_column(df, col, TYPE)

                except IndexError:
                    logger.warning(f'{col} not found in the dictionary file.')

    return df.sort_index().reset_index(drop=True)


def format_numeric_column(dataframe, column_name, TYPE):
    '''Format column in dataframe to specified TYPE and convert to string.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Pandas DataFrame with AGS4 data
    column_name : str
        Name of column to be formatted
    TYPE : str
        AGS4 TYPE for specified column

    Returns
    -------
    Pandas DataFrame
        Dataframe with formatted data.
    '''

    df = dataframe.copy()
    col = column_name

    try:
        if 'DP' in TYPE:
            i = int(TYPE.strip('DP'))
            # Apply formatting DATA rows with real numbers. NaNs will be avoided so that they will be exported
            # as "" rather than "nan"
            mask = (df.HEADING == "DATA") & df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].apply(lambda x: f"{x:.{i}f}")

        elif 'SCI' in TYPE:
            i = int(TYPE.strip('SCI'))
            # Apply formatting DATA rows with real numbers. NaNs will be avoided so that they will be exported
            # as "" rather than "nan"
            mask = (df.HEADING == "DATA") & df[col].notna()
            df.loc[mask, col] = df.loc[mask, col].apply(lambda x: f"{x:.{i}E}")

        elif 'SF' in TYPE:

            # Apply formatting DATA rows with real numbers. NaNs will be avoided so that they will be exported
            # as "" rather than "nan"
            mask = (df.HEADING == "DATA") & df[col].notna()
            df.loc[mask, [col]] = df.loc[mask, [col]].map(lambda x: _format_SF(x, TYPE))

        else:
            pass

    except ValueError:
        logger.warning(f"Numeric data in {col:<9} not reformatted as it had one or more non-numeric entries.")

    except TypeError:
        logger.warning(f"Numeric data in {col:<9} not reformatted as it had one or more non-numeric entries.")

    return df


def _format_SF(value, TYPE):
    '''Format a value to specified number of significant figures
    and return a string.'''

    from math import log10, floor

    # Avoid log(0) as int(log(0)) will raise an OverflowError
    if value != 0:
        i = int(TYPE.strip('SF')) - 1 - int(floor(log10(abs(value))))

    else:
        return f"{value}"

    if i < 0:
        return f"{round(value, i):.0f}"

    else:
        return f"{value:.{i}f}"


def check_file(filepath_or_buffer, standard_AGS4_dictionary=None, rename_duplicate_headers=True, encoding='utf-8'):
    """Validate AGS4 file against AGS4 rules.

    Parameters
    ----------
    filepath_or_buffer : strFile path (str, pathlib.Path), or StringIO.
        Path to AGS4 file or any object with a read() method (such as an open
        file or StringIO) to be checked.
    standard_AGS4_dict : str
        Path to .ags file with standard AGS4 dictionary or version number
        (should be one of '4.1.1', '4.1', '4.0.4', '4.0.3', '4.0').
    rename_duplicate_headers: bool, default=True
        Rename duplicate headers if found. Neither AGS4 tables nor Pandas
        dataframes allow duplicate headers, therefore a number will be appended
        to duplicates to make them unique.
    encoding : str, default='utf-8'
        Encoding of text file.

    Returns
    -------
    dict
        Dictionary contains AGS4 error in input file.
    """

    import hashlib
    from python_ags4 import check

    ags_errors = {}

    # Line checks
    if _is_file_like(filepath_or_buffer):
        f = filepath_or_buffer
        f.seek(0)
        if hasattr(f, 'encoding') and getattr(f, 'encoding', None) != encoding and hasattr(f, 'reconfigure'):
            f.reconfigure(encoding=encoding)
        close_file = False
    else:
        f = open(filepath_or_buffer, "r", newline='', encoding=encoding, errors="replace")
        close_file = True

    try:
        # Preflight check for AGS3 files and to calculate SHA256 hash of file
        sha256_hash = hashlib.sha256()

        for i, line in enumerate(f, start=1):
            ags_errors = check.is_ags3_like(line, i, ags_errors=ags_errors)

            # Exit if ags3_like line is found
            if ('AGS Format Rule 3' in ags_errors) and ('AGS3' in ags_errors['AGS Format Rule 3'][0]['desc']):
                ags_errors = check.add_error_msg(ags_errors, 'Validator Process Error', '-', '',
                                                 'Validation terminated due to suspected AGS3 file. Please fix errors and try again.')
                return ags_errors

            # Perform SHA256 checksum calculation
            sha256_hash.update(line.encode(encoding))

        # Reset file stream to the beginning to start AGS4 checks
        f.seek(0)

        # Initiate group name and headings list
        group = ''
        headings = []

        logger.info('Checking lines...')

        for i, line in enumerate(f, start=1):

            # Track headings to be used with group checks
            if line.strip('"').startswith("GROUP"):
                # Reset group name and headings list at the beginning each group
                group = ''
                headings = []

                try:
                    group = line.rstrip().strip('"').split('","')[1]

                except IndexError:
                    # GROUP name not available (Rule 19 should catch this error)
                    pass

            elif line.strip('"').startswith("HEADING"):
                headings = line.rstrip().split('","')
                headings = [item.strip('"') for item in headings]

            # Call line Checks
            ags_errors = check.rule_1(line, i, ags_errors=ags_errors, encoding=encoding)
            ags_errors = check.rule_2a(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_3(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_4_1(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_4_2(line, i, group=group, headings=headings, ags_errors=ags_errors)
            ags_errors = check.rule_5(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_6(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_7_1(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_19(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_19a(line, i, group=group, ags_errors=ags_errors)
            ags_errors = check.rule_19b_1(line, i, group=group, ags_errors=ags_errors)

        # Add additional information about how Rule 1 is implemented if infringements are detected
        if 'AGS Format Rule 1' in ags_errors:
            msg = "AGS4 Rule 1 is interpreted as allowing both standard ASCII characters (Unicode code points 0-127) "\
                  "and extended ASCII characters (Unicode code points 160-255). "\
                  "Please beware that extended ASCII characters differ based on the encoding used when the file was created. "\
                  "The validator defaults to 'utf-8' encoding as it is the most widely used encoding compatible with Unicode. "\
                  "The user can override this default if the file encoding is different but, "\
                  "it is highly recommended that the 'utf-8' encoding be used when creating AGS4 files. "\
                  "(Hint: If not 'utf-8', then the encoding is most likely to be 'windows-1252' aka 'cp1252')"
            ags_errors = check.add_error_msg(ags_errors, 'General', '', '', msg)

        # Import data into Pandas dataframes to run group checks
        logger.info('Loading tables...')

        f.seek(0)
        tables, headings, line_numbers = AGS4_to_dataframe(f, get_line_numbers=True, rename_duplicate_headers=rename_duplicate_headers)

        # Group Checks
        logger.info('Checking headings and groups...')

        ags_errors = check.rule_2(tables, headings, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_2b(tables, headings, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_8(tables, headings, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_12(tables, headings, ags_errors=ags_errors)
        ags_errors = check.rule_13(tables, headings, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_14(tables, headings, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_15(tables, headings, line_numbers, ags_errors=ags_errors)

        # Not able to locate any other files in same folder for an already opened file/stream:
        if close_file:
            ags_errors = check.rule_20(tables, headings, filepath_or_buffer, ags_errors=ags_errors)

        ags_errors = check.is_TRAN_AGS_valid(tables, headings, line_numbers, ags_errors=ags_errors)

        # Dictionary Based Checks

        # Pick path to standard dictionary
        if standard_AGS4_dictionary in [None, '4.1.1', '4.1', '4.0.4', '4.0.3', '4.0']:
            # Filepath to the standard dictionary will be picked based on version
            # number if a valid version number is provided. If it is not specified
            # at all, then the filepath will be selected based on the value of
            # TRAN_AGS in the TRAN table.
            standard_AGS4_dictionary = check.pick_standard_dictionary(tables=tables, dict_version=standard_AGS4_dictionary)

        # Import standard dictionary file into Pandas dataframes
        tables_std_dict, _ = AGS4_to_dataframe(standard_AGS4_dictionary)

        # Combine standard dictionary with DICT table in input file to create an extended dictionary
        # This extended dictionary is used to check the file schema
        dictionary = check.combine_DICT_tables(tables_std_dict, tables)

        logger.info('Checking file schema...')

        ags_errors = check.rule_7_2(headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_9(headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_10a(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_10b(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_10c(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_11(tables, headings, dictionary, ags_errors=ags_errors)
        ags_errors = check.rule_16(tables, headings, dictionary, ags_errors=ags_errors)
        ags_errors = check.rule_17(tables, headings, dictionary, ags_errors=ags_errors)
        # Note: rule_18() has to be called after rule_9() as it relies on rule_9() to flag non-standard headings.
        ags_errors = check.rule_18(tables, headings, ags_errors=ags_errors)
        ags_errors = check.rule_19b_2(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
        ags_errors = check.rule_19b_3(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)

        # Warnings
        # TO BE ADDED

        # FYI
        ags_errors = check.fyi_16_1(tables, headings, tables_std_dict['ABBR'], ags_errors=ags_errors)

        # Add summary of data
        for val in check.get_data_summary(tables):
            ags_errors = check.add_error_msg(ags_errors, 'Summary of data', '', '', val)

    except AGS4Error as err:
        logger.exception(err)

        ags_errors = check.add_error_msg(ags_errors, 'General', '-', '',
                                         'Could not complete validation. Please fix listed errors and try again.')
        ags_errors = check.add_error_msg(ags_errors, 'Validator Process Error', '-', '', str(err))

    except UnboundLocalError as err:
        logger.exception(err)

        # The presence of a byte-order-mark (BOM) in the same row as first
        # "GROUP" line can cause this exception. This will be caught by line
        # checks for Rule 1 (since the BOM is not an ASCII character) and Rule 3
        # (since the BOM precedes the string "GROUP"). The BOM encoding can be
        # ignored by setting the 'encoding' argument to 'utf-8-sig'.
        f.seek(0)

        tables, headings, line_numbers = AGS4_to_dataframe(f, encoding='utf-8-sig',
                                                           get_line_numbers=True, rename_duplicate_headers=rename_duplicate_headers)

        # Add warning to error log
        msg = 'This file seems to be encoded with a byte-order-mark (BOM). It is highly recommended that the '\
              'file be saved without BOM encoding to avoid issues with other software.'
        ags_errors = check.add_error_msg(ags_errors, 'General', '', '', msg)

    except Exception as err:
        logger.exception(err)

        ags_errors = check.add_error_msg(ags_errors, 'General', '-', '',
                                         'Could not complete validation. Please fix listed errors and try again.')
        ags_errors = check.add_error_msg(ags_errors, 'Validator Process Error', '-', '', str(err))

    finally:
        if close_file:
            f.close()

        # Add metadata
        ags_errors = check.add_meta_data(filepath_or_buffer, standard_AGS4_dictionary, ags_errors=ags_errors,
                                         encoding=encoding)

        if ('AGS Format Rule 3' in ags_errors) and ('AGS3' in ags_errors['AGS Format Rule 3'][0]['desc']):
            # If AGS3 file is detected, the for loop in which the SHA256 hash is
            # calculated will be terminated, therefore report it as "Not calculated"
            ags_errors = check.add_error_msg(ags_errors, 'Metadata', 'SHA256 hash', '', 'Not calculated')

        else:
            ags_errors = check.add_error_msg(ags_errors, 'Metadata', 'SHA256 hash', '', sha256_hash.hexdigest())

        return ags_errors


# Helper functions/classes #

def write_error_report(ags_errors, output_file, show_warnings=False, show_fyi=False):
    '''Save error report to file.

    Parameters
    ----------
    ags_errors : dict
        Python dictionary with AGS4 errors. Output from AGS4.check_file().
    output_file : str
        Path to output file
    show_warnings : bool, default=False
        Include warning messages in error report
    show_fyi : bool, default=False
        Include FYI messages in error report

    Returns
    -------
    None
    '''

    import textwrap

    error_count, warnings_count, fyi_count = count_errors(ags_errors)

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Write metadata
            if 'Metadata' in ags_errors.keys():
                for entry in ags_errors['Metadata']:
                    f.write(f'''{entry['line']+':':<12} {entry['desc']}\r\n''')
                f.write('\r\n')

            # Summary of errors log
            if error_count == 0:
                f.write('All checks passed!\r\n')
                f.write('\r\n')

            elif ('AGS Format Rule 3' in ags_errors) and ('AGS3' in ags_errors['AGS Format Rule 3'][0]['desc']):
                f.write('Checking aborted as AGS3 files are not supported!\r\n')
                f.write('\r\n')

            else:
                f.write(f'{error_count} error(s) found in file!\r\n')
                f.write('\r\n')

            # Write summary of warnings and FYI messages
            if show_warnings:
                f.write(f'{warnings_count} warning(s) returned.\r\n')
                f.write('\r\n')

            if show_fyi:
                f.write(f'{fyi_count} FYI message(s) returned.\r\n')
                f.write('\r\n')

            # Write 'General' error messages first if present
            if 'General' in ags_errors.keys():
                f.write('General:')
                for entry in ags_errors['General']:
                    msg = '\r\n  '.join(textwrap.wrap(entry['desc'], width=100))
                    f.write(f'''\r\n  {msg}\r\n''')
                f.write('\r\n')

            # Print 'Summary of data' if present
            if 'Summary of data' in ags_errors.keys():
                f.write('Summary of data:\r\n')
                for entry in ags_errors['Summary of data']:
                    msg = '\r\n  '.join(textwrap.wrap(entry['desc'], width=100))
                    f.write(f'''  {msg}\r\n''')
                f.write('\r\n')

            # Write other AGS Format error messages
            for key in [x for x in ags_errors if 'AGS Format Rule' in x]:
                f.write(f'{key}:\r\n')
                for entry in ags_errors[key]:
                    f.write(f'''  Line {entry['line']:<8} {entry['group'].strip('"'):<7} {entry['desc']}\r\n''')
                f.write('\r\n')

            # Write parsing and process error messages
            for key in [x for x in ags_errors if 'Validator Process Error' in x]:
                f.write(f'{key}:\r\n')
                for entry in ags_errors[key]:
                    f.write(f'''  Line {entry['line']:<8} {entry['group'].strip('"'):<7} {entry['desc']}\r\n''')
                f.write('\r\n')

            # Write warning messages
            if show_warnings is True:
                for key in [x for x in ags_errors if 'Warning' in x]:
                    f.write(f'{key}:\r\n')
                    for entry in ags_errors[key]:
                        f.write(f'''  Line {entry['line']:<8} {entry['group'].strip('"'):<7} {entry['desc']}\r\n''')
                    f.write('\r\n')

            # Write FYI messages
            if show_fyi is True:
                for key in [x for x in ags_errors if 'FYI' in x]:
                    f.write(f'{key}:\r\n')
                    for entry in ags_errors[key]:
                        f.write(f'''  Line {entry['line']:<8} {entry['group'].strip('"'):<7} {entry['desc']}\r\n''')
                    f.write('\r\n')

        logger.info(f'Error report saved in {output_file}')

    except FileNotFoundError:
        logger.error('Invalid output file path. Error report could not be saved. '
                     'Please ensure that the specified directory exists.')

    except TypeError:
        # Nothing to do if output_file is None
        pass


def count_errors(ags_errors):
    '''Count number of errors, warnings, and FYI messages in error log.

    Parameters
    ----------
    ags_errors : dict
        Python dictionary with AGS4 errors. Output from AGS4.check_file().

    Returns
    -------
    error_count : int
        Number of error messages
    warnings_count : int
        Number of warning messages
    fyi_count : int
        Number of FYI messages
    '''

    # Count number of entries in error log
    error_count = 0
    warnings_count = 0
    fyi_count = 0
    for key, val in ags_errors.items():
        error_count += len(val) if ('AGS Format Rule' in key) or ('Validator Process Error' in key) else 0
        warnings_count += len(val) if 'Warning' in key else 0
        fyi_count += len(val) if 'FYI' in key else 0

    return error_count, warnings_count, fyi_count


def sort_groups(tables, sorting_strategy='dictionary'):
    """Sort groups/tables parsed from AGS4 file.

    Parameters
    ----------
    tables : dict of dataframes
        Dictionary of Pandas dataframes (output from 'AGS4_to_dataframe()')
    sorting_strategy : {'dictionary', 'alphabetical', 'hierarchical'}, default='dictionary'
        Sort groups in the order in which they appear in the dictionary, the
        hierarchy defined in the dictionary, or alphabetically.

    Returns
    -------
    dict
        Dictionary of Pandas dataframes (output from 'AGS4_to_dataframe()')
    """

    from .check import pick_standard_dictionary, combine_DICT_tables

    # Combine standard dictionary with DICT table in input file to create an extended dictionary
    # This extended dictionary is used to check the table order
    standard_AGS4_dictionary = pick_standard_dictionary(tables=tables)
    tables_std_dict, _ = AGS4_to_dataframe(standard_AGS4_dictionary)
    dictionary = combine_DICT_tables(tables_std_dict, tables)

    if sorting_strategy == 'dictionary':
        group_list = dictionary.query(" DICT_TYPE.eq('GROUP') ")['DICT_GRP'].to_list()

    elif sorting_strategy == 'alphabetical':
        group_list = sorted(tables.keys())

    elif sorting_strategy == 'hierarchical':
        # Initiate hierarchical group list with groups with no parents
        # (NOTE: LBST is the child of LBSG but is included to avoid second
        # recursive search)
        group_list = ['PROJ', 'TRAN',  'ABBR', 'DICT', 'FILE', 'TYPE', 'UNIT',
                      'LBSG', 'LBST', 'PREM', 'STND']

        # Recursive function to walk through dictionary in hierarchical order
        # and return list of groups.
        def get_child_groups_sorted_by_hierarchy(DICT, group, group_list=[]):
            for item in DICT.query(" DICT_TYPE.eq('GROUP') & DICT_PGRP.eq(@group) ")['DICT_GRP']\
                            .to_list():
                group_list.append(item)
                get_child_groups_sorted_by_hierarchy(DICT, item, group_list)

            return group_list

        # Get all child groups under 'PROJ' group
        group_list = get_child_groups_sorted_by_hierarchy(dictionary, 'PROJ', group_list)

    # Assemble sorted tables
    sorted_tables = {x: tables[x] for x in group_list if x in tables.keys()}

    # Issue warning if groups are missing after sorting and append them to the
    # end in alphabetical order
    for item in sorted(set(tables.keys()).difference(set(sorted_tables.keys()))):
        msg = f'WARNING:Table {item} appended to the end as it was either not found in the dictionary '\
              'or its parent group is not defined under DICT_PGRP.'
        logger.warning(f"{msg}")
        sorted_tables[item] = tables[item]

    return sorted_tables


def _is_file_like(obj):
    """Check if object is file like

    Returns
    -------
    bool
        Return True if obj is file like, otherwise return False
    """

    if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
        return False

    if not hasattr(obj, "__iter__"):
        return False

    return True


def _is_bytebuffer(obj):
    """Check if object is buffer like

    Returns
    -------
    bool
        Return True if obj is buffer like, otherwise return False
    """

    if hasattr(obj, 'decode'):
        return True

    return False


class AGS4Error(Exception):
    """Exception class for AGS4 parsing errors.
    """
    pass
