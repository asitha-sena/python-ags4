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


from pandas import DataFrame, to_numeric


def AGS4_to_dict(filepath, encoding='utf-8'):
    """Load all the data in a AGS4 file to a dictionary of dictionaries.
    This GROUP in the AGS4 file is assigned its own dictionary.

    'AGS4_to_dataframe' uses this funtion to load AGS4 data in to Pandas
    dataframes.

    Input:
    -----
    filepath   - Path to AGS4 file

    Output:
    ------
    data       - Python dictionary populated with data from the AGS4 file
                    with AGS4 headers as keys
    headings   - Dictionary with the headings in the each GROUP
                 (This will be needed to recall the correct column order when
                 writing pandas dataframes back to AGS4 files.
                 i.e. input for 'dataframe_to_AGS4()' function)
    """

    # Read file with errors="replace" to catch UnicodeDecodeErrors
    with open(filepath, "r", encoding=encoding, errors="replace") as f:
        data = {}

        # dict to save and output the headings. This is not really necessary
        # for the read AGS4 function but will be needed to write the columns
        # of pandas dataframes when writing them back to AGS4 files.
        # (The HEADING column needs to be the first column in order to preserve
        # the AGS data format. Other columns in certain groups have a
        # preferred order as well)

        headings = {}

        for line in f:
            temp = line.rstrip().split('","')
            temp = [item.strip('"') for item in temp]

            if temp[0] == 'GROUP':
                group = temp[1]
                data[group] = {}

            elif temp[0] == 'HEADING':
                headings[group] = temp

                for item in temp:
                    data[group][item] = []

            elif temp[0] in ['TYPE', 'UNIT', 'DATA']:
                for i in range(0, len(temp)):
                    data[group][headings[group][i]].append(temp[i])

            else:
                continue

    return data, headings


def AGS4_to_dataframe(filepath, encoding='utf-8'):
    """Load all the tables in a AGS4 file to a Pandas dataframes. The output is
    a Python dictionary of dataframes with the name of each AGS4 table (i.e.
    GROUP) as the primary key.

    Input:
    -----
    filepath    - Path to AGS4 file

    Output:
    ------
    data        - Python dictionary populated with Pandas dataframes. Each
                  GROUP in the AGS4 files is assigned to its a dataframe.
    headings    -  Dictionary with the headings in the each GROUP
                   (This will be needed to recall the correct column order when
                   writing pandas dataframes back to AGS4 files.
                   i.e. input for 'dataframe_to_AGS4()' function)

    """

    # Extract AGS4 file into a dictionary of dictionaries
    data, headings = AGS4_to_dict(filepath, encoding=encoding)

    # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
    df = {}
    for key in data:
        df[key] = DataFrame(data[key])

    return df, headings


def dataframe_to_AGS4(data, headings, filepath, mode='w', index=False, encoding='utf-8'):
    """Write Pandas dataframes that have been extracted using
    'AGS4_to_dataframe()' function back to an AGS4 file.

    Input:
    -----
    data        - Dictionary of Pandas dataframes (output from
                    'AGS4_to_dataframe()')
    headings -    Dictionary of lists containing AGS4 headings in the correct order
                  (e.g. output from 'AGS4_to_dataframe()')
                  Columns can be dropped as well from the exported file using
                  this option. An empty dictionary {} can be passed to export
                  data without explicitly ensuring column order.
    filepath    - Path to output file
    mode        - Option to write ('w') or append ('a') data ('w' by default)
    index       - Include the index column when writing to file. (False by default)
                  WARNING: The output will not be a valid AGS4 file if set to True.

    Output:
    ------
    AGS4 file with data in the dictionary of dataframes that is input.
    """

    # Open file and write/append data
    with open(filepath, mode, newline='') as f:
        for key in data:

            try:
                columns = headings[key]

                f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')
                data[key].to_csv(f, index=index, quoting=1, columns=columns, line_terminator='\r\n', encoding=encoding)
                f.write("\r\n")

            except KeyError:
                print(f"*Warning*: Input 'headings' dictionary does not have a entry named {key}.")
                print(f"           All columns in the {key} table will be exported in the default order.")
                print("           Please check column order and ensure AGS4 Rule 7 is still satisfied.")

                f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')
                data[key].to_csv(f, index=index, quoting=1, line_terminator='\r\n', encoding=encoding)
                f.write("\r\n")


def convert_to_numeric(dataframe):
    """The AGS4_to_dataframe() function extracts the data from an AGS4 file and
    puts each table into a Pandas DataFrame as text. This function reads the
    TYPE row and coverts the columns with data types 0DP, 1DP, 2DP, 3DP, 4DP,
    5DP, and MC into numerical data. This allows the data to be plotted and
    used in calculations/formulas.

    Input:
    -----
    dataframe    - Pandas DataFrame outputted by AGS4.AGS4_to_dataframe()
                   function

    Output:
    ------
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


def convert_to_text(dataframe, dictionary):
    """Convert AGS4 DataFrame with numeric columns back to formatted text ready for exporting.

    Input:
    -----
    dataframe  - Pandas DataFrame with numeric columns. e.g. output from AGS4.convert_to_numeric()
    dictionary - AGS4 dictionary file from which to get UNIT and TYPE rows and to convert to
                 numeric fields to required precision

    Output:
    ------
    Pandas DataFrame.

    e.g.
    >>from python_ags4 import AGS4
    >>
    >>tables, headings = AGS4.AGS4_to_dataframe('Data.ags')
    >>LOCA_numeric = AGS4.convert_to_numeric(tables['LOCA])
    >>
    >>LOCA_text = convert_to_text(LOCA, 'DICT.ags')
    """

    # Reindex input dataframe
    df = dataframe.copy().reset_index(drop=True)

    # Read dictionary file
    temp, _ = AGS4_to_dataframe(dictionary)
    DICT = temp['DICT']

    for col in df.columns:

        if col == 'HEADING':
            df.loc[-2, 'HEADING'] = 'UNIT'
            df.loc[-1, 'HEADING'] = 'TYPE'

        else:

            try:
                TYPE = DICT.loc[DICT.DICT_HDNG == col, 'DICT_DTYP'].iloc[0]
                UNIT = DICT.loc[DICT.DICT_HDNG == col, 'DICT_UNIT'].iloc[0]

                if 'DP' in TYPE:
                    i = int(TYPE[0])
                    df.loc[0:, col] = df.loc[0:, col].apply(lambda x: f"{x:.{i}f}")

                elif 'SCI' in TYPE:
                    i = int(TYPE[0])
                    df.loc[0:, col] = df.loc[0:, col].apply(lambda x: f"{x:.{i}e}")

                # TODO: Add formatting for data type 'nSF'
                # elif 'SF' in TYPE:

                df.loc[-2, col] = UNIT
                df.loc[-1, col] = TYPE

            except IndexError:
                print(f"*WARNING*:{col} not found in the dictionary file.")

    return df.sort_index()


def AGS4_to_excel(input_file, output_file, encoding='utf-8'):
    """Load all the tables in a AGS4 file to an Excel spreasheet.

    Input:
    -----
    input_file    - Path to AGS4 file
    output_file   - Path to Excel file

    Output:
    ------
    Excel file populated with data from the input AGS4 file.
    """

    from pandas import ExcelWriter

    # Extract AGS4 file into a dictionary of dictionaries
    tables, headings = AGS4_to_dataframe(input_file, encoding=encoding)

    # Write to Excel file
    with ExcelWriter(output_file) as writer:
        for key in tables:
            tables[key].to_excel(writer, sheet_name=key, index=False)


def excel_to_AGS4(input_file, output_file):
    """Export AGS4 data in Excel file to .ags file.

    Input:
    -----
    input_file    - Path to Excel file
                    (Note: Each GROUP should be in a separate worksheet.
                     e.g. output from AGS4.AGS4_to_excel)
    output_file   - Path to AGS4 file

    Output:
    ------
    AGS4 file with data from the input Excel file.
    """

    from pandas import read_excel

    # Read data from Excel file in to DataFrames
    tables = read_excel(input_file, sheet_name=None, engine='openpyxl')

    # Export dictionary of DataFrames to AGS4 file
    # TODO: Add column formatting and ordering
    dataframe_to_AGS4(tables, {}, output_file)
