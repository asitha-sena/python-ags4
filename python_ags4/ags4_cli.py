#!/usr/bin/env python

import click
from python_ags4 import AGS4, __version__
from rich.console import Console
import os

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
@click.option('-f', '--format_columns', default="true",
              help='Format numeric data based on TYPE values if converting from .xlsx to .ags (true [default] or false)')
@click.option('-d', '--dictionary', type=click.File('r'), default=None,
              help="Path to AGS4 dictionary file. Numeric data will be formatted based on TYPE values from this file if converting from .xlsx to .ags.")
def convert(input_file, output_file, format_columns, dictionary):
    '''Convert .ags file to .xlsx file or vice versa.

    INPUT_FILE   Path to input file. The file should be either .ags or .xlsx

    OUTPUT_FILE  Path to output file. The file should be either .ags or .xlsx

    e.g.

    Linux/Mac: ags4_cli convert ~/temp/data.ags ~/temp/data.xlsx

    Windows:   ags4_cli convert c:\Temp\data.ags c:\Temp\data.xlsx

    '''

    try:
        if input_file.endswith('.ags') & output_file.endswith('.xlsx'):
            console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
            console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
            print('')

            AGS4.AGS4_to_excel(input_file, output_file)

            console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

        elif input_file.endswith('.xlsx') & output_file.endswith('.ags'):
            console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
            console.print(f'[green]Exporting data to... [bold]{output_file}[/bold][/green]')
            print('')

            # Process optional arguments
            format_numeric_columns = format_columns.lower() in ['true', 'yes']

            if dictionary is not None:
                dictionary = dictionary.name

            # Call export function
            AGS4.excel_to_AGS4(input_file, output_file, format_numeric_columns=format_numeric_columns, dictionary=dictionary)

            console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

        elif (input_file.endswith('.ags') & output_file.endswith('.ags')) | (input_file.endswith('.xlsx') & output_file.endswith('.xlsx')):
            file_type = input_file.split('.')[-1]
            console.print(f'[yellow]Both input and output files are of the same type (i.e. [bold].{file_type}[/bold]). No conversion necessary.[/yellow]')

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


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('-o', '--output_file', type=click.Path(writable=True), default=None,
              help="Path to save error log")
@click.option('-d', '--dictionary', type=click.Path(exists=True), default=None,
              help="Path to AGS4 dictionary file.")
def check(input_file, dictionary, output_file):
    '''Check .ags file for error based AGS4 rules.

    INPUT_FILE   Path to .ags file to be checked
    '''

    if input_file.endswith('.ags'):
        console.print(f'[green]Running [bold]python_ags4 v{__version__}[/bold][/green]')
        console.print(f'[green]Opening file... [bold]{input_file}[/bold][/green]')
        console.print('')

        ags_errors = AGS4.check_file(input_file, standard_AGS4_dictionary=dictionary)

        # Dictionay evaluates to False if empty
        if bool(ags_errors) is False:
            console.print('\n[green]File check complete! No errors found.[/green]\n')

            if output_file is not None:
                save_to_file(output_file, ags_errors, input_file, 'No')

        else:
            # Count number of entries in error log
            error_count = 0
            for key, val in ags_errors.items():
                if 'Rule' in key:
                    error_count += len(val)

            # Print errors to screen if list is short enough.
            if error_count < 100:
                print_to_screen(ags_errors)

                console.print(f'\n[yellow]File check complete! {error_count} errors found![/yellow]')

                if output_file is not None:
                    save_to_file(output_file, ags_errors, input_file, error_count)

            else:
                console.print(f'\n[yellow]File check complete! {error_count} errors found![/yellow]')
                console.print('\n[yellow]Error report too long to print to screen.[/yellow]')

                if output_file is None:
                    output_dir = os.path.dirname(input_file)
                    output_file = os.path.join(output_dir, 'error_log.txt')

                save_to_file(output_file, ags_errors, input_file, error_count)

    else:
        console.print('[red]ERROR: Only .ags files are accepted as input.[/red]')


def print_to_screen(ags_errors):
    '''Print error report to screen.'''

    console.print('')

    # Print  metadata
    if 'Metadata' in ags_errors.keys():
        for entry in ags_errors['Metadata']:
            click.echo(f'''{entry['line']}: \t {entry['desc']}''')
        console.print('')

    # Print 'General' error messages first if present
    if 'General' in ags_errors.keys():
        console.print('[underline]General[/underline]:')

        for entry in ags_errors['General']:
            console.print(f'''  {entry['desc']}''')
        console.print('')

    # Print other error messages
    for key in [x for x in ags_errors if 'Rule' in x]:
        console.print(f'''[white underline]{key}[/white underline]:''')
        for entry in ags_errors[key]:
            console.print(f'''  Line {entry['line']}\t [bold]{entry['group'].strip('"')}[/bold]\t {entry['desc']}''')
        console.print('')


def save_to_file(output_file, ags_errors, input_file, error_count):
    '''Save error report to file.'''

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Write metadata
            if 'Metadata' in ags_errors.keys():
                for entry in ags_errors['Metadata']:
                    f.write(f'''{entry['line']}: \t {entry['desc']}\n''')
                f.write('\n')

            # Write 'General' error messages first if present
            if 'General' in ags_errors.keys():
                f.write('General:\n')
                for entry in ags_errors['General']:
                    f.write(f'''  {entry['desc']}\n''')
                f.write('\n')

            # Write other error messages
            for key in [x for x in ags_errors if 'Rule' in x]:
                f.write(f'{key}:\n')
                for entry in ags_errors[key]:
                    f.write(f'''  Line {entry['line']}\t {entry['group'].strip('"')}\t {entry['desc']}\n''')
                f.write('\n')

            if error_count == 'No':
                console.print(f'[green]Report saved in {output_file}[/green]\n')
            else:
                console.print(f'\n[yellow]Error report saved in {output_file}[/yellow]\n')

    except FileNotFoundError:
        console.print('[red]\nERROR: Invalid output file path. Error report could not be saved.[/red]')
        console.print('[red]       Please ensure that the specified directory exists.[/red]')


if __name__ == '__main__':
    main()
