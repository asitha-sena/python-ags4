# Copyright Asitha Senanayake

from pandas import DataFrame, to_numeric


def AGS4_to_dict(filepath):
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
    with open(filepath, "r", errors="replace") as f:
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


def AGS4_to_dataframe(filepath):
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
    data, headings = AGS4_to_dict(filepath)

    # Convert dictionary of dictionaries to a dictionary of Pandas dataframes
    df = {}
    for key in data:
            df[key] = DataFrame(data[key])

    return df, headings


def dataframe_to_AGS4(data, headings, filepath, mode='w', index=False):
    """Write Pandas dataframes that have been extracted using
    'AGS4_to_dataframe()' function back to an AGS4 file.

    Input:
    -----
    data        - Dictionary of Pandas dataframes (output from
                    'AGS4_to_dataframe()')
    headings    - Dictionary of AGS4 headings in the correct order
                    (output from 'AGS4_to_dataframe()')
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
            f.write('"GROUP"'+","+'"'+key+'"'+'\r\n')
            data[key].to_csv(f, index=index, quoting=1, columns=headings[key], line_terminator='\r\n')
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
    >>from AGS4 import AGS4
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
