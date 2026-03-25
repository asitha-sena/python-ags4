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

from pandas import DataFrame, concat, read_json

from .AGS4 import AGS4Error


def get_DICT_table_from_json_file(filepath):
    '''Convert AGS4 dictionary in .json format to DICT table in .ags format.

    The official standard dictionaries in .json format is available at
    https://gitlab.com/AGS-DFWG-Web/ASG4

    Parameters
    ----------
    filepath : str
        Path to JSON file

    Returns
    -------
    Pandas DataFrame with DICT table

    '''

    # Extract heading DICT_TYPE='HEADING' rows from JSON data
    heading_rows = read_json(filepath).rename(columns={'group': 'DICT_GRP',
                                                       'heading': 'DICT_HDNG',
                                                       'suggested_type': 'DICT_DTYP',
                                                       'description': 'DICT_DESC',
                                                       'suggested_unit': 'DICT_UNIT',
                                                       'example': 'DICT_EXMP'})\
                                      .pipe(lambda df: df.assign(HEADING='DATA',
                                                                 DICT_TYPE='HEADING',
                                                                 DICT_STAT=df.heading_status.map({'*': 'KEY',
                                                                                                  'R': 'REQUIRED',
                                                                                                  '*R': 'KEY+REQUIRED',
                                                                                                  'R*': 'KEY+REQUIRED',
                                                                                                  '': 'OTHER',
                                                                                                  'Deprecated': 'DEPRECATED'}),
                                                                 DICT_PGRP='',
                                                                 DICT_REM='',
                                                                 FILE_FSET='',
                                                                 in_group_order=df.in_group_order.astype('int'),
                                                                 group_order=df.group_order.astype('int')))

    # Extract heading DICT_TYPE='GROUP' rows from JSON data
    group_rows = heading_rows.groupby('DICT_GRP').first()\
                             .reset_index()\
                             .drop('DICT_DESC', axis=1)\
                             .rename(columns={'group_description': 'DICT_DESC'})\
                             .pipe(lambda df: df.assign(HEADING='DATA',
                                                        DICT_TYPE='GROUP',
                                                        DICT_HDNG='',
                                                        DICT_STAT='',
                                                        DICT_DTYP='',
                                                        DICT_UNIT='',
                                                        DICT_EXMP='',
                                                        DICT_PGRP=df['parent'],
                                                        FILE_FSET='',
                                                        in_group_order=0))

    # Create UNIT and TYPE rows
    unit_and_type_rows = DataFrame({'HEADING': ['UNIT', 'TYPE'],
                                    'DICT_TYPE': ['', 'PA'],
                                    'DICT_GRP': ['', 'X'],
                                    'DICT_HDNG': ['', 'X'],
                                    'DICT_STAT': ['', 'PA'],
                                    'DICT_DTYP': ['', 'PT'],
                                    'DICT_DESC': ['', 'X'],
                                    'DICT_UNIT': ['', 'PU'],
                                    'DICT_EXMP': ['', 'X'],
                                    'DICT_PGRP': ['', 'X'],
                                    'DICT_REM': ['', 'X'],
                                    'FILE_FSET': ['', 'X'],
                                    'group_order': [-1, 0]})

    # Combine all rows
    DICT = concat([unit_and_type_rows, heading_rows, group_rows])

    # Mark deprecated groups and headings
    mask = DICT.group_status.eq('Deprecated')
    DICT.loc[mask & DICT.DICT_TYPE.eq('GROUP'), 'DICT_STAT'] = 'DEPRECATED'

    # Sort rows and keep only relevant columns
    DICT = DICT.sort_values(by=['group_order', 'in_group_order'])\
               .loc[:, ['HEADING', 'DICT_TYPE', 'DICT_GRP', 'DICT_HDNG', 'DICT_STAT', 'DICT_DTYP', 'DICT_DESC', 'DICT_UNIT', 'DICT_EXMP',
                        'DICT_PGRP', 'DICT_REM', 'FILE_FSET']]\
               .reset_index(drop=True)\

    # Found some linebreak characters in the descriptions that are not needed in DICT_DESC
    # Replace them with spaces
    DICT.loc[:, 'DICT_DESC'] = DICT.DICT_DESC.str.replace(r'(\r\n)', '', regex=True)
    DICT.loc[:, 'DICT_DESC'] = DICT.DICT_DESC.str.replace(r'(\n)', '', regex=True)

    # Some DICT_DESC entries in the json file are enclosed by double quotes.
    # These need to be either single quotes or double double quotes according to
    # AGS4 Rule 5. The library correctly handles this when writing the DICT table
    # to a .ags file but it was decided to replace double quotes with single
    # quotes to be consistent with the existing built-in standard dictionary
    # files
    DICT.loc[:, 'DICT_DESC'] = DICT.DICT_DESC.str.replace(r'(")', '\'', regex=True)

    return DICT


def get_ABBR_table_from_json_file(filepath, filepath_ELRG, version='4.1'):
    '''Convert AGS4 abbreviations in .json format to ABBR table in .ags format.

    The official ABBR list in .json format is available at
    https://gitlab.com/AGS-DFWG-Web/ASG4

    Parameters
    ----------
    filepath : str
        Path to JSON file with AGS4 abbreviations list
    filepath_ELRG : str or None
        Path to JSON file with ELRG_CODE list
    version : {'4.0', '4.1'}
        Version of standard dictionary.

    Returns
    -------
    Pandas DataFrame with ABBR table

    '''

    # Check version provided by user
    if version not in ['4.0', '4.1']:
        raise AGS4Error("Invalid version number. Only '4.0' and '4.1' are valid entries.")

    # Extract heading "DATA" rows from JSON data with abbreviations list
    data_rows = read_json(filepath).rename(columns={'Group': 'ABBR_HDNG', 'Code': 'ABBR_CODE', 'Description': 'ABBR_DESC'})\
                                   .assign(HEADING='DATA', ABBR_LIST=version, ABBR_REM='', FILE_FSET='')\
                                   .query("Version.str.contains(@version) & Status.str.contains('Approved', case=False)")\
                                   .sort_values(by=['ABBR_HDNG', 'ABBR_CODE'])

    # Create UNIT and TYPE rows
    unit_and_type_rows = DataFrame({'HEADING': ['UNIT', 'TYPE'],
                                    'ABBR_HDNG': ['', 'X'],
                                    'ABBR_CODE': ['', 'X'],
                                    'ABBR_DESC': ['', 'X'],
                                    'ABBR_LIST': ['', 'X'],
                                    'ABBR_REM': ['', 'X'],
                                    'FILE_FSET': ['', 'X']})

    # Extract ELRG_CODE list
    if filepath_ELRG is not None:
        elrg_codes = read_json(filepath_ELRG).rename(columns={'code': 'ABBR_CODE', 'description': 'ABBR_DESC'})\
                                    .assign(HEADING='DATA', ABBR_HDNG='ELRG_CODE', ABBR_LIST=version, ABBR_REM='', FILE_FSET='')\
                                    .query("version.str.contains(@version) & status.str.contains('Approved', case=False)")\
                                    .sort_values(by=['ABBR_HDNG', 'ABBR_CODE'])

    else:
        elrg_codes = DataFrame()

    # Combine all rows
    ABBR = concat([unit_and_type_rows, data_rows, elrg_codes])

    # Sort columns and reset index
    ABBR = ABBR.loc[:, ['HEADING', 'ABBR_HDNG', 'ABBR_CODE', 'ABBR_DESC', 'ABBR_LIST', 'ABBR_REM', 'FILE_FSET']]\
               .reset_index(drop=True)

    return ABBR


def get_TYPE_table_from_json_file(filepath, version='4.1'):
    '''Convert AGS4 abbreviations in .json format to TYPE table in .ags format.

    The official TYPE list in .json format is available at
    https://gitlab.com/AGS-DFWG-Web/ASG4

    Parameters
    ----------
    filepath : str
        Path to JSON file
    version : {'4.0', '4.1'}
        Version of standard dictionary.

    Returns
    -------
    Pandas DataFrame with ABBR table

    '''

    # Check version provided by user
    if version not in ['4.0', '4.1']:
        raise AGS4Error("Invalid version number. Only '4.0' and '4.1' are valid entries.")

    # Extract heading "DATA" rows from JSON data
    data_rows = read_json(filepath).rename(columns={'Type': 'TYPE_TYPE', 'Desc': 'TYPE_DESC'})\
                                   .assign(HEADING='DATA', FILE_FSET='')\
                                   .query("Version.str.contains(@version)")\
                                   .sort_values(by=['TYPE_TYPE', 'TYPE_DESC'])

    # Create UNIT and TYPE rows
    unit_and_type_rows = DataFrame({'HEADING': ['UNIT', 'TYPE'],
                                    'TYPE_TYPE': ['', 'X'],
                                    'TYPE_DESC': ['', 'X'],
                                    'FILE_FSET': ['', 'X']})

    # Combine all rows
    TYPE = concat([unit_and_type_rows, data_rows])\

    # Sort columns and reset index
    TYPE = TYPE.loc[:, ['HEADING', 'TYPE_TYPE', 'TYPE_DESC', 'FILE_FSET']]\
               .reset_index(drop=True)\

    return TYPE


def get_UNIT_table_from_json_file(filepath, version='4.1'):
    '''Convert AGS4 abbreviations in .json format to UNIT table in .ags format.

    The official UNIT list in .json format is available at
    https://gitlab.com/AGS-DFWG-Web/ASG4

    Parameters
    ----------
    filepath : str
        Path to JSON file
    version : {'4.0', '4.1'}
        Version of standard dictionary.

    Returns
    -------
    Pandas DataFrame with ABBR table

    '''

    # Check version provided by user
    if version not in ['4.0', '4.1']:
        raise AGS4Error("Invalid version number. Only '4.0' and '4.1' are valid entries.")

    # Extract heading "DATA" rows from JSON data
    data_rows = read_json(filepath).rename(columns={'Unit': 'UNIT_UNIT', 'Description': 'UNIT_DESC'})\
                                   .assign(HEADING='DATA', UNIT_REM='', FILE_FSET='')\
                                   .query("Version.str.contains(@version) & Status.str.contains('Approved', case=False)")\
                                   .pipe(lambda df: df.drop_duplicates(subset='UNIT_UNIT', keep='first'))\
                                   .sort_values(by=['UNIT_UNIT', 'UNIT_DESC'], key=lambda x: x.str.lower())

    # The 'key' argument is used in sort_values() to apply the sorting after
    # changing all entries to lower case. This is necessary because
    # sort_values() is case sensitive by default, with uppercase letters having
    # higher precedence than lower case letters.

    # Create UNIT and TYPE rows
    unit_and_type_rows = DataFrame({'HEADING': ['UNIT', 'TYPE'],
                                    'UNIT_UNIT': ['', 'X'],
                                    'UNIT_DESC': ['', 'X'],
                                    'UNIT_REM': ['', 'X'],
                                    'FILE_FSET': ['', 'X']})

    # Combine all rows
    UNIT = concat([unit_and_type_rows, data_rows])\

    # Sort columns and reset index
    UNIT = UNIT.loc[:, ['HEADING', 'UNIT_UNIT', 'UNIT_DESC', 'UNIT_REM', 'FILE_FSET']]\
               .reset_index(drop=True)\

    return UNIT
