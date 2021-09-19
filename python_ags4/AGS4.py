# Copyright (C) 2020-2021  Asitha Senanayake
#
# This file is part of python_ags4.
#
# python_ags4 is free software: you can redistribute it and/or modify
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


# Read functions #

def AGS4_to_dict(filepath_or_buffer, encoding='utf-8', get_line_numbers=False):
    """Load all the data in a AGS4 file to a dictionary of dictionaries.
    This GROUP in the AGS4 file is assigned its own dictionary.

    'AGS4_to_dataframe' uses this funtion to load AGS4 data in to Pandas
    dataframes.

    Parameters
    ----------
    filepath_or_buffer : File path (str, pathlib.Path), or StringIO.
        Path to AGS4 file or any object with a read() method (such as an open file or StringIO).
    encoding : str
        Encoding of text file (default 'utf-8')
    get_line_numbers : bool
        Add line number column to each table (for UNIT, TYPE, and DATA rows) and return
        a dictionary with line numbers for GROUP and HEADING lines (default False)

    Returns
    -------
    data : dict
        Python dictionary populated with data from the AGS4 file with AGS4 headers as keys
    headings : dict
        Dictionary with the headings in the each GROUP (This will be needed to
        recall the correct column order when writing pandas dataframes back to AGS4
        files. i.e. input for 'dataframe_to_AGS4()' function)
    line_numbers : dict (Only if get_line_numbers=True)
        Dictionary with the starting line numbers of GROUP and HEADING rows. This is only
        required for checking a .ags file with 'check_file() function.
    """

    from rich import print as rprint
    import sys

    if is_file_like(filepath_or_buffer):
        f = filepath_or_buffer
        close_file = False
    else:
        # Read file with errors="replace" to catch UnicodeDecodeErrors
        f = open(filepath_or_buffer, "r", encoding=encoding, errors="replace")
        close_file = True

    try:

        data = {}

        # dict to save and output the headings. This is not really necessary
        # for the read AGS4 function but will be needed to write the columns
        # of pandas dataframes when writing them back to AGS4 files.
        # (The HEADING column needs to be the first column in order to preserve
        # the AGS data format. Other columns in certain groups have a
        # preferred order as well)

        headings = {}
        line_numbers = {}

        for i, line in enumerate(f, start=1):
            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            if temp[0] == 'GROUP':
                group = temp[1]
                data[group] = {}

                # Store GROUP line number
                # (A default 'HEADING' entry is added to avoid KeyErrors in case of missing
                # HEADING rows)
                line_numbers[group] = {'GROUP': i, 'HEADING': '-'}

            elif temp[0] == 'HEADING':

                # Catch HEADER rows with duplicate entries as it will result in a dictionary with
                # arrays of unequal lengths and cause a ValueError when trying to convert to a
                # Pandas DataFrame
                if len(temp) != len(set(temp)):
                    rprint(f"[yellow]  WARNING: HEADER row in [bold]{group}[/bold] (Line {i}) has duplicate entries.[/yellow]")

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

                            rprint(f'[blue]  INFO: Duplicate column {item} found and renamed as {item}_{count}.[/blue]')
                            rprint('[blue]        Automatically renamed columns do not conform to AGS4 Rules 19a and 19b.[/blue]')
                            rprint('[blue]        Therefore, please review the data and rename or drop duplicate columns as appropriate.[/blue]')

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

                # Check whether line has the same number of entries as the number of headings in the group
                # If not, print error and exit
                if len(temp) != len(headings[group]):
                    rprint(f"[red]  Error: Line {i} does not have the same number of entries as the HEADING row in [bold]{group}[/bold].[/red]")
                    sys.exit()

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


def AGS4_to_dataframe(filepath_or_buffer, encoding='utf-8', get_line_numbers=False):
    """Load all the tables in a AGS4 file to a Pandas dataframes. The output is
    a Python dictionary of dataframes with the name of each AGS4 table (i.e.
    GROUP) as the primary key.

    Parameters
    ----------
    filepath_or_buffer : str, StringIO
        Path to AGS4 file or any file like object (open file or StringIO)
    show_line_number : bool
        Add line number column to each table (default False)
    get_line_numbers : bool
        Add line number column to each table (for UNIT, TYPE, and DATA rows) and return
        a dictionary with line numbers for GROUP and HEADING lines (default False)

    Returns
    -------
    data : dict
        Python dictionary populated with Pandas dataframes. Each GROUP in the AGS4 files is assigned to its a dataframe.
    headings : dict
        Dictionary with the headings in the each GROUP (This will be needed to
        recall the correct column order when writing pandas dataframes back to AGS4
        files. i.e. input for 'dataframe_to_AGS4()' function)
    line_numbers : dict (Only if get_line_numbers=True)
        Dictionary with the starting line numbers of GROUP and HEADING rows. This is only
        required for checking a .ags file with 'check_file() function.
    """

    from pandas import DataFrame

    # Extract AGS4 file into a dictionary of dictionaries
    # A dictionary with group line numbers is returned, in addition to data and headings, for checking purposes
    if get_line_numbers is True:
        data, headings, line_numbers = AGS4_to_dict(filepath_or_buffer, encoding=encoding, get_line_numbers=get_line_numbers)

        # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
        df = {}
        for key in data:
            df[key] = DataFrame(data[key])

        return df, headings, line_numbers

    # Otherwise only the data and the headings are returned
    data, headings = AGS4_to_dict(filepath_or_buffer, encoding=encoding)

    # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
    df = {}
    for key in data:
        df[key] = DataFrame(data[key])

    return df, headings


def AGS4_to_excel(input_file, output_file, encoding='utf-8'):
    """Load all the tables in a AGS4 file to an Excel spreasheet.

    Parameters
    ----------
    input_file : str
        Path to AGS4 file
    output_file : str
        Path to Excel file

    Returns
    -------
    Excel file populated with data from the input AGS4 file.
    """

    from pandas import ExcelWriter
    from rich import print as rprint

    # Extract AGS4 file into a dictionary of dictionaries
    tables, headings = AGS4_to_dataframe(input_file, encoding=encoding)

    # Write to Excel file
    with ExcelWriter(output_file) as writer:
        for key in tables:
            rprint(f'[green]Writing data from... [bold]{key}[/bold][/green]')

            # Check table size and issue warning for large files that could crash the program
            if 25000 < tables[key].shape[0] < 100000:
                rprint(f'[blue]  INFO: {key} has {tables[key].shape[0]} rows, so it will take about a minute to export.[/blue]')
            elif tables[key].shape[0] > 100000:
                rprint(f'[yellow]  WARNING: {key} has {tables[key].shape[0]} rows, so it may take a few minutes to export.[/yellow]')
                rprint('[yellow]           The program will terminate if it runs out of memory in the process.[/yellow]')

            tables[key].to_excel(writer, sheet_name=key, index=False)


# Write functions #

def dataframe_to_AGS4(data, headings, filepath, mode='w', index=False, encoding='utf-8', warnings=True):
    """Write Pandas dataframes that have been extracted using
    'AGS4_to_dataframe()' function back to an AGS4 file.

    Parameters
    ----------
    data : dict
        Dictionary of Pandas dataframes (output from 'AGS4_to_dataframe()')
    headings : dict
        Dictionary of lists containing AGS4 headings in the correct order (e.g.
        output from 'AGS4_to_dataframe()') Columns can be dropped as well from
        the exported file using this option. An empty dictionary {} can be
        passed to export data without explicitly ensuring column order.
    filepath : str
        Path to output file
    mode : str, optional
        Option to write ('w') or append ('a') data ('w' by default)
    index : bool, optional
        Include the index column when writing to file. (False by default)
        WARNING: The output will not be a valid AGS4 file if set to True.

    Returns
    -------
    AGS4 file with data in the dictionary of dataframes that is input.
    """

    from rich import print as rprint

    # Open file and write/append data
    with open(filepath, mode, newline='', encoding=encoding) as f:
        for key in data:

            try:
                columns = headings[key]

                rprint(f'[green]Writing data from... [bold]{key}[/bold][green]')
                f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')
                data[key].apply(lambda x: x.str.replace('""', '"'))\
                         .to_csv(f, index=index, quoting=1, columns=columns, line_terminator='\r\n', encoding=encoding)
                # The lambda funtion is applied to the dataframe to take care of
                # an edge case where quoted text is present in a field. The
                # to_csv function automatiically adds an extra pair of quotes
                # around any quoted strings that is encountered and there is not
                # way work around for it as of Pandas v1.1.5. Therefore,
                # double-double quotes required by AGS4 Rule 5 are changed to
                # single-double quotes before the to_csv function is called.
                # This ensures that the output file has the quoted string in
                # double-double quotes.
                f.write("\r\n")

            except KeyError:

                rprint(f'[green]Writing data from... [bold]{key}[/bold][green]')

                if warnings is True:
                    rprint(f"[yellow]  WARNING: Input 'headings' dictionary does not have a entry named [bold]{key}[/bold].[/yellow]")
                    rprint(f"[italic yellow]           All columns in the {key} table will be exported in the default order.[/italic yellow]")
                    rprint("[italic yellow]           Please check column order and ensure AGS4 Rule 7 is still satisfied.[/italic yellow]")

                f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')
                data[key].apply(lambda x: x.str.replace('""', '"')).to_csv(f, index=index, quoting=1, line_terminator='\r\n', encoding=encoding)
                f.write("\r\n")


def excel_to_AGS4(input_file, output_file, format_numeric_columns=True, dictionary=None):
    """Export AGS4 data in Excel file to .ags file.

    Parameters
    ----------
    input_file : str
        Path to Excel file (Note: Each GROUP should be in a separate worksheet.
        e.g. output from AGS4.AGS4_to_excel)
    output_file : str
        Path to AGS4 file
    reformat_numeric_columns : bool, optional
        Format numeric columns to match specified TYPE
    dictionary : str
        Filepath to dictionary if the UNIT and TYPE data in tables need to be
        overridden.

    Returns
    -------
    AGS4 file with data from the input Excel file.
    """

    from pandas import read_excel
    from rich import print as rprint

    # Read data from Excel file in to DataFrames
    tables = read_excel(input_file, sheet_name=None, engine='openpyxl')

    # Format numeric columns
    if format_numeric_columns is True:

        for key in tables:
            # First drop columns with non-compliant names (AGS Rule 19)
            columns_to_drop = []

            for col_name in tables[key].columns:
                if col_name == 'HEADING':
                    pass
                elif col_name.isupper() & (len(col_name) <= 9) & (len(col_name.split('_')[0]) <= 4):
                    pass
                else:
                    columns_to_drop.append(col_name)
                    rprint(f'[yellow]  WARNING: Column [bold]{col_name}[/bold] dropped as name does not conform to AGS4 Rule 19.[/yellow]')

            tables[key].drop(columns=columns_to_drop, inplace=True)

            # Then drop rows without a proper HEADING
            tables[key] = tables[key].loc[tables[key].HEADING.isin(['UNIT', 'TYPE', 'DATA']), :]

            # Finally format numeric column
            rprint(f'[green]Formatting columns in... [bold]{key}[/bold][/green]')
            tables[key] = convert_to_text(tables[key], dictionary=dictionary)

    # Export dictionary of DataFrames to AGS4 file
    dataframe_to_AGS4(tables, {}, output_file, warnings=False)


# Formatting functions #

def convert_to_numeric(dataframe):
    """The AGS4_to_dataframe() function extracts the data from an AGS4 file and
    puts each table into a Pandas DataFrame as text. This function reads the
    TYPE row and coverts the columns with data types 0DP, 1DP, 2DP, 3DP, 4DP,
    5DP, and MC into numerical data. This allows the data to be plotted and
    used in calculations/formulas.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Pandas DataFrame outputted by AGS4.AGS4_to_dataframe() function

    Returns
    -------
    A Pandas DataFrame with numerical columns to converted from
    text to numeric datatypes, the TYPE and UNIT rows (i.e. rows 1 and 2)
    removed, and the index reset.

    e.g.
    >>from python_ags4 import AGS4
    >>
    >>data, headings = AGS4.AGS4_to_dataframe(filepath)
    >>
    >>LNMC = AGS4.convert_to_numeric(data['LNMC'])
    """

    from pandas import to_numeric

    # First create a copy of the DataFrame to avoid overwriting the
    # original data
    df = dataframe.copy()

    # Convert to appropriate columns to numeric
    numeric_df = df.loc[:, df.iloc[1].str.contains('DP|MC|SF|SCI')].apply(to_numeric, errors='coerce')

    # Replace columns in input dataframe with numeric columns
    df[numeric_df.columns] = numeric_df

    # Remove TYPE and UNIT rows and reset index
    df = df.iloc[2:, :].reset_index(drop=True)

    return df


def convert_to_text(dataframe, dictionary=None):
    """Convert AGS4 DataFrame with numeric columns back to formatted text ready for exporting
    back to a csv file.

    Parameters
    ----------
    dataframe : Pandas DataFrame
        Pandas DataFrame with numeric columns. e.g. output from
        AGS4.convert_to_numeric()
    dictionary : str, optional
        Path to AGS4 dictionary file from which to get UNIT and TYPE rows and to
        convert to numeric fields to required precision. The values from the
        dictionary will override those already in the UNIT and TYPE rows in the
        dataframe.

    Returns
    -------
    Pandas DataFrame

    e.g.
    >>from python_ags4 import AGS4
    >>
    >>tables, headings = AGS4.AGS4_to_dataframe('Data.ags')
    >>LOCA_numeric = AGS4.convert_to_numeric(tables['LOCA])
    >>
    >>LOCA_text = convert_to_text(LOCA, 'DICT.ags')
    """

    import sys
    from rich import print as rprint

    # Make copy of dataframe and reset index to make sure numbering
    # starts from zero
    df = dataframe.copy().reset_index(drop=True)

    # Check whether to use UNIT and TYPE rows in dataframe or to
    # retrieve values from the dictionary file
    if dictionary is None:
        try:
            # Check whether dataframe has "UNIT" and "TYPE" rows
            assert 'UNIT' in df.HEADING.values
            assert 'TYPE' in df.HEADING.values

            for col in df.columns:
                TYPE = df.loc[df.HEADING == 'TYPE', col].values[0]
                df = format_numeric_column(df, col, TYPE)

        except AssertionError:
            rprint("[red]  ERROR: Cannot convert to text as UNIT and/or TYPE row(s) are missing.")
            rprint("[red]         Please provide dictonary file or add UNIT & TYPE rows to input file to proceed.[/red]")
            sys.exit()

    else:
        # Read dictionary file
        temp, _ = AGS4_to_dataframe(dictionary)
        DICT = temp['DICT']

        # Check whether UNIT and TYPE rows are already in dataframe
        UNIT_row_present = 'UNIT' in df.HEADING.values
        TYPE_row_present = 'TYPE' in df.HEADING.values

        # Format columns and add UNIT/TYPE rows if necessary
        for col in df.columns:

            if col == 'HEADING':

                if not UNIT_row_present:
                    df.loc[-2, 'HEADING'] = 'UNIT'

                if not TYPE_row_present:
                    df.loc[-1, 'HEADING'] = 'TYPE'

            else:

                try:
                    # Get type and unit from dictionary
                    TYPE = DICT.loc[DICT.DICT_HDNG == col, 'DICT_DTYP'].iloc[0]
                    UNIT = DICT.loc[DICT.DICT_HDNG == col, 'DICT_UNIT'].iloc[0]

                    if UNIT_row_present:
                        # Overwrite existing UNIT with one from the dictionary
                        df.loc[df.HEADING == 'UNIT', col] = UNIT
                    else:
                        # Add UNIT row if one is not already there
                        df.loc[-2, col] = UNIT

                    if TYPE_row_present:
                        # Overwrite existing TYPE with one from the dictionary
                        df.loc[df.HEADING == 'TYPE', col] = TYPE
                    else:
                        # Add TYPE row if one is not already there
                        df.loc[-1, col] = TYPE

                    df = format_numeric_column(df, col, TYPE)

                except IndexError:
                    rprint(f"[yellow]  WARNING: [bold]{col}[/bold] not found in the dictionary file.[/yellow]")

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
        Pandas DataFrame with formatted data.
    '''

    from rich import print as rprint

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
            df.loc[mask, col] = df.loc[mask, col].apply(lambda x: f"{x:.{i}e}")

        elif 'SF' in TYPE:

            # Apply formatting DATA rows with real numbers. NaNs will be avoided so that they will be exported
            # as "" rather than "nan"
            mask = (df.HEADING == "DATA") & df[col].notna()
            df.loc[mask, [col]] = df.loc[mask, [col]].applymap(lambda x: _format_SF(x, TYPE))

        else:
            pass

    except ValueError:
        rprint(f"[yellow]  WARNING: Numeric data in [bold]{col:<9}[/bold] not reformatted as it had one or more non-numeric entries.[/yellow]")

    except TypeError:
        rprint(f"[yellow]  WARNING: Numeric data in [bold]{col:<9}[/bold] not reformatted as it had one or more non-numeric entries.[/yellow]")

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


def check_file(input_file, standard_AGS4_dictionary=None):
    """This function checks the input AGS4 file for errors.

    Parameters
    ----------
    input_file : str
        Path to AGS4 file (*.ags) to be checked
    standard_AGS4_dict : str
        Path to .ags file with standard AGS4 dictionary

    Returns
    -------
    dict
        Dictionary contains AGS4 error in input file.
    """

    from python_ags4 import check
    from rich import print as rprint
    import traceback

    ags_errors = {}

    # Line checks
    with open(input_file, 'r', newline='', encoding='utf-8', errors='replace') as f:

        # Initiate group name and headings list
        group = ''
        headings = []

        rprint('[green]  Checking lines...[/green]')
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
            ags_errors = check.rule_1(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_2a(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_2c(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_3(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_4a(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_4b(line, i, group=group, headings=headings, ags_errors=ags_errors)
            ags_errors = check.rule_5(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_6(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_19(line, i, ags_errors=ags_errors)
            ags_errors = check.rule_19a(line, i, group=group, ags_errors=ags_errors)
            ags_errors = check.rule_19b_1(line, i, group=group, ags_errors=ags_errors)

    # Import file into Pandas DataFrame to run group checks
    try:
        rprint('[green]  Loading tables...[/green]')
        tables, headings, line_numbers = AGS4_to_dataframe(input_file, get_line_numbers=True)

    except:
        # TODO: Add specific errors to except clause to conform to flake8
        err = traceback.format_exc()
        rprint('[red] ERROR: Could not continue with group checks on file. Please review error log and fix line errors first.[/red]')
        rprint(f'[red]\n{err}[/red]')
        return ags_errors

    # Group Checks
    rprint('[green]  Checking headings and groups...[/green]')
    ags_errors = check.rule_2(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_2b(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_8(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_12(tables, headings, ags_errors=ags_errors)
    ags_errors = check.rule_13(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_14(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_15(tables, headings, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_20(tables, headings, input_file, ags_errors=ags_errors)

    # Dictionary Based Checks

    # Pick standard dictionary
    if standard_AGS4_dictionary is None:
        standard_AGS4_dictionary = check.pick_standard_dictionary(tables)

    # Import standard dictionary into Pandas DataFrames
    tables_std_dict, _ = AGS4_to_dataframe(standard_AGS4_dictionary)

    # Combine standard dictionary with DICT table in input file to create an extended dictionary
    # This extended dictionary is used to check the file schema
    dictionary = check.combine_DICT_tables(tables_std_dict, tables)

    rprint('[green]  Checking file schema...[/green]')
    ags_errors = check.rule_7(headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_9(headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_10a(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_10b(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_10c(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_11(tables, headings, dictionary, ags_errors=ags_errors)
    ags_errors = check.rule_16(tables, headings, dictionary, ags_errors=ags_errors)
    ags_errors = check.rule_17(tables, headings, dictionary, ags_errors=ags_errors)
    # Note: rule_18() has to be called after rule_9() as it relies on rule_9() to flag non-standard headings.
    ags_errors = check.rule_18(tables, headings, ags_errors=ags_errors)
    ags_errors = check.rule_19b_2(headings, dictionary, line_numbers, ags_errors=ags_errors)
    ags_errors = check.rule_19c(tables, headings, dictionary, line_numbers, ags_errors=ags_errors)

    # Check if file is likely to in AGS3 format
    ags_errors = check.is_ags3(tables, input_file, ags_errors=ags_errors)

    # Add metadata
    ags_errors = check.add_meta_data(input_file, standard_AGS4_dictionary, ags_errors=ags_errors)

    return ags_errors


def is_file_like(obj):
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
