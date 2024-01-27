#!/usr/bin/env python

# Copyright (C) 2020-2024  Asitha Senanayake
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


import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import textwrap

import click
from rich.console import Console

from python_ags4 import AGS4, __version__

# Add warnings filter because Pandas 2.1 produces a lot of deprecation warnings
import warnings
warnings.filterwarnings('ignore')

# Create rich console for pretty printing
console = Console()


@click.group()
def main():
    '''A tool to read, write, and check AGS4 files.
    '''
    pass


@main.command()
@click.argument('input_file', type=click.Path('r'))
@click.argument('output_file', type=click.Path(writable=True))
@click.option('-f', '--format_columns', type=click.BOOL, default=True,
              help='Format numeric data based on TYPE values if converting from .xlsx to .ags (default True)')
@click.option('-d', '--dictionary', type=click.File('r'), default=None,
              help="Path to AGS4 dictionary file. "
                   "Numeric data will be formatted based on TYPE values from this file if converting from .xlsx to .ags.")
@click.option('-r', '--rename_duplicate_headers', type=click.BOOL, default=True,
              help="Rename duplicate headers when converting to Excel (default True)")
@click.option('-s', '--sorting_strategy', type=click.Choice(['hierarchical', 'alphabetical', 'dictionary']),
              help="Sort worksheets in Excel file. (WARNING: Original table/group order will be lost)")
@click.option('-l', '--log_messages', is_flag=True,
              help='Log all messages to python_ags4.log file (default False)')
def convert(input_file, output_file, format_columns, dictionary, rename_duplicate_headers, sorting_strategy, log_messages):
    r'''Convert .ags file to .xlsx file or vice versa.

    INPUT_FILE   Path to input file. The file should be either .ags or .xlsx

    OUTPUT_FILE  Path to output file. The file should be either .ags or .xlsx

    e.g.

    Linux/Mac: ags4_cli convert ~/temp/data.ags ~/temp/data.xlsx

    Windows:   ags4_cli convert c:\Temp\data.ags c:\Temp\data.xlsx

    Exit codes:
        0 - Conversion succeeded
        1 - Conversion failed
    '''

    # Log messages if specified
    if log_messages is True:
        logging.basicConfig(format='{asctime}  {levelname:<8}  {module}.{funcName:<20}  {message}',
                            style='{', datefmt='%Y-%m-%dT%H:%M:%S%z',
                            level=logging.DEBUG,
                            handlers=[RotatingFileHandler(filename=Path(input_file).parent/'python_ags4.log', maxBytes=100e3, backupCount=1)])

    else:
        logging.basicConfig(level=logging.CRITICAL)

    try:
        if input_file.endswith('.ags') & output_file.endswith('.xlsx'):
            console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
            console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
            print('')

            AGS4.AGS4_to_excel(input_file, output_file, rename_duplicate_headers=rename_duplicate_headers,
                               sorting_strategy=sorting_strategy)
            console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')
            sys.exit(0)

        elif input_file.endswith('.xlsx') & output_file.endswith('.ags'):
            console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
            console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
            print('')

            if dictionary is not None:
                dictionary = dictionary.name

            # Call export function
            AGS4.excel_to_AGS4(input_file, output_file, format_numeric_columns=format_columns,
                               dictionary=dictionary)

            console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')
            sys.exit(0)

        elif (input_file.endswith('.ags') & output_file.endswith('.ags')) | (input_file.endswith('.xlsx') & output_file.endswith('.xlsx')):
            file_type = input_file.split('.')[-1]
            console.print(f'[yellow]Both input and output files are of the same type (i.e. [bold].{file_type}[/bold]). '
                          'No conversion necessary.[/yellow]')

        elif input_file.endswith('.ags'):
            console.print('[red]Please provide an output file with a [bold].xlsx[/bold] extension.[/red]')

        elif input_file.endswith('.xlsx'):
            console.print('[red]Please provide an output file with a [bold].ags[/bold] extension.[/red]')

        elif output_file.endswith('.ags'):
            console.print('[red]Please provide an input file with a [bold].xlsx[/bold] extension.[/red]')

        elif output_file.endswith('.xlsx'):
            console.print('[red]Please provide an input file with a [bold].ags[/bold] extension.[/red]')

        else:
            input_file_type = input_file.split('.')[-1]
            console.print(f'[red]ERROR: This program cannot convert [bold].{input_file_type}[/bold] files.[/red]')
            console.print('')
            console.print('[yellow]Try "ags4_cli convert --help" to see help and examples.[/yellow]')

    except FileNotFoundError:
        console.print('[red]ERROR: Invalid output file path. Converted file could not be saved.[/red]')
        console.print('[red]       Please ensure that the specified directory exists.[/red]')

    except AGS4.AGS4Error:
        pass

    # All error cases exit here
    sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output_file', type=click.Path(writable=True), default=None,
              help="Path to save error log")
@click.option('-d', '--dictionary_path', type=click.File('r'), default=None,
              help="Path to AGS4 dictionary file.")
@click.option('-v', '--dictionary_version',
              type=click.Choice(['4.1.1', '4.1', '4.0.4', '4.0.3', '4.0']),
              help='Version of standard dictionary to use. (Warning: Overrides version specified in TRAN_AGS '
                   'and custom dictionary specifed by --dictionary_path)')
@click.option('-e', '--encoding',
              type=click.Choice(['utf-8', 'windows-1252', 'cp1252']), default='utf-8',
              help='File encoding (default utf-8)')
@click.option('-l', '--log_messages', is_flag=True,
              help='Log all messages to python_ags4.log file (default False)')
@click.option('-w', '--show_warnings', is_flag=True,
              help='Show warnings in addition to errors.')
@click.option('-f', '--show_fyi', is_flag=True,
              help='Show FYI message in addition to errors.')
def check(input_file, output_file, dictionary_path, dictionary_version, encoding, log_messages, show_warnings, show_fyi):
    '''Check .ags file for errors according to AGS4 rules.

    INPUT_FILE   Path to .ags file to be checked

    Exit codes:
        0 - All checks passed
        1 - Errors found or file read error
    '''

    # Log messages if specified
    if log_messages is True:
        logging.basicConfig(format='{asctime}  {levelname:<8}  {module}.{funcName:<20}  {message}',
                            style='{', datefmt='%Y-%m-%dT%H:%M:%S%z',
                            level=logging.DEBUG,
                            handlers=[RotatingFileHandler(filename=Path(input_file).parent/'python_ags4.log', maxBytes=100e3, backupCount=1)])

    else:
        logging.basicConfig(level=logging.CRITICAL)

    # Run validation
    if input_file.lower().endswith('.ags'):
        console.print(f'[green]Running [bold]python_ags4 v{__version__}[/bold][/green]')
        console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
        console.print('')

        # Get input info from arguments and options
        if dictionary_version:
            standard_AGS4_dictionary = dictionary_version

        elif dictionary_path:
            standard_AGS4_dictionary = dictionary_path.name

        else:
            standard_AGS4_dictionary = None

        # Try to check file
        try:
            ags_errors = AGS4.check_file(input_file,
                                         standard_AGS4_dictionary=standard_AGS4_dictionary,
                                         encoding=encoding)

        # End here with unsuccessful exit code if an exception is raised
        except AGS4.AGS4Error:
            sys.exit(1)

        # Count number of entries in error log
        error_count, warnings_count, fyi_count = AGS4.count_errors(ags_errors)
        total_msg_count = error_count + warnings_count*show_warnings + fyi_count*show_fyi

        if (total_msg_count > 100) and output_file is None:
            output_file = Path(input_file).parent / 'error_log.txt'

        # Print/save error report
        print_to_screen(ags_errors, show_warnings, show_fyi)
        AGS4.write_error_report(ags_errors, output_file, show_warnings, show_fyi)

        if error_count == 0:
            sys.exit(0)

    else:
        console.print('[red]ERROR: Only .ags files are accepted as input.[/red]')

    # Any errors in file or other problems will exit with failure code
    sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path('r'))
@click.argument('output_file', type=click.Path(writable=True))
@click.option('-s', '--sorting_strategy', type=click.Choice(['hierarchical', 'alphabetical', 'dictionary']),
              default='hierarchical',
              help="Sorting strategy.")
@click.option('-l', '--log_messages', is_flag=True,
              help='Log all messages to python_ags4.log file (default False)')
def sort(input_file, output_file, sorting_strategy, log_messages):
    '''Sort groups/tables in .ags file and create copy.

    INPUT_FILE   Path to input .ags file

    OUTPUT_FILE  Path to output .ags file

    Exit codes:
        0 - All checks passed
        1 - Errors found or file read error
    '''

    # Log messages if specified
    if log_messages is True:
        logging.basicConfig(format='{asctime}  {levelname:<8}  {module}.{funcName:<20}  {message}',
                            style='{', datefmt='%Y-%m-%dT%H:%M:%S%z',
                            level=logging.DEBUG,
                            handlers=[RotatingFileHandler(filename=Path(input_file).parent/'python_ags4.log', maxBytes=100e3, backupCount=1)])

    else:
        logging.basicConfig(level=logging.CRITICAL)

    try:
        if input_file.endswith('.ags') & output_file.endswith('.ags'):
            console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
            tables, headings = AGS4.AGS4_to_dataframe(input_file)

            console.print(f'[green]Sorting tables... [/green]')
            print('')
            sorted_tables = AGS4.sort_groups(tables, sorting_strategy)

            console.print(f'[green]Writing to... [bold]{output_file}[/bold][/green]')
            AGS4.dataframe_to_AGS4(sorted_tables, headings, output_file)
            console.print('\n[green]Files with sorted groups/tables created! :heavy_check_mark:[/green]\n')
            sys.exit(0)

        else:
            console.print('[red]Please provide input and output files with a [bold].ags[/bold] extension.[/red]')

    except FileNotFoundError:
        console.print('[red]ERROR: Invalid output file path. Converted file could not be saved.[/red]')
        console.print('[red]       Please ensure that the specified directory exists.[/red]')

    except AGS4.AGS4Error:
        pass

    # All error cases exit here
    sys.exit(1)


def print_to_screen(ags_errors, show_warnings=False, show_fyi=False):
    '''Print error report to screen.'''

    console.print('')

    error_count, warnings_count, fyi_count = AGS4.count_errors(ags_errors)
    total_msg_count = error_count + warnings_count*show_warnings + fyi_count*show_fyi

    # Print  metadata
    if 'Metadata' in ags_errors.keys():
        for entry in ags_errors['Metadata']:
            click.echo(f'''{entry['line']}: \t {entry['desc']}''')
        console.print('')

    # Print full report only if total message count is less than or equal to 100
    if total_msg_count <= 100:
        # Print 'General' error messages first if present
        if 'General' in ags_errors.keys():
            console.print('[underline]General[/underline]:')

            for entry in ags_errors['General']:
                msg = '\r\n  '.join(textwrap.wrap(entry['desc'], width=100))
                console.print(f'''  {msg}''')
                console.print('')

        # Print 'Summary of data' if present
        if 'Summary of data' in ags_errors.keys():
            console.print('[underline]Summary of data[/underline]:')
            for entry in ags_errors['Summary of data']:
                msg = '\r\n  '.join(textwrap.wrap(entry['desc'], width=100))
                console.print(f'''  {msg}''')
            console.print('')

        # Write other AGS Format error messages
        for key in [x for x in ags_errors if 'AGS Format Rule' in x]:
            console.print(f'''[white underline]{key}[/white underline]:''')
            for entry in ags_errors[key]:
                console.print(f'''  Line {entry['line']}\t [bold]{entry['group'].strip('"')}[/bold]\t {entry['desc']}''')
            console.print('')

        # Print warnings
        if show_warnings is True:
            for key in [x for x in ags_errors if 'Warning' in x]:
                console.print(f'''[white underline]{key}[/white underline]:''')
                for entry in ags_errors[key]:
                    console.print(f'''  Line {entry['line']}\t [bold]{entry['group'].strip('"')}[/bold]\t {entry['desc']}''')
                console.print('')

        # Print FYI messages
        if show_fyi is True:
            for key in [x for x in ags_errors if 'FYI' in x]:
                console.print(f'''[white underline]{key}[/white underline]:''')
                for entry in ags_errors[key]:
                    console.print(f'''  Line {entry['line']}\t [bold]{entry['group'].strip('"')}[/bold]\t {entry['desc']}''')
                console.print('')

    # Print summary
    if error_count == 0:
        console.print('[green]File check complete![/green]')
        console.print(f'[green]  {error_count} Errors[/green]')

    else:
        console.print('[yellow]File check complete![/yellow]')
        console.print(f'[yellow]  {error_count} Errors[/yellow]')

    if warnings_count == 0 and show_warnings:
        console.print(f'[green]  {warnings_count} Warnings[/green]')

    elif show_warnings:
        console.print(f'[yellow]  {warnings_count} Warnings[/yellow]')

    if fyi_count == 0 and show_fyi:
        console.print(f'[green]  {fyi_count} FYI messages[/green]')

    elif show_fyi:
        console.print(f'[yellow]  {fyi_count} FYI messages[/yellow]')


if __name__ == '__main__':
    main()
