#!/usr/bin/env python

import click
from python_ags4 import AGS4
from rich.console import Console

# Create rich console for pretty printing
console = Console()


@click.group()
def main():
    '''A tool to read and write AGS4 files.
    '''
    pass


@main.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w', lazy=False))
# The lazy=False option is used in order to catch errors in the output file path before starting the program
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

    input_file = input_file.name
    output_file = output_file.name

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
        AGS4.excel_to_AGS4(input_file, output_file, format_numeric_columns=format_numeric_columns,
                           dictionary=dictionary)

        console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

    elif (input_file.endswith('.ags') & output_file.endswith('.ags')) | (input_file.endswith('.xlsx') & output_file.endswith('.xlsx')):
        file_type = input_file.split('.')[-1]
        console.print(f'[yellow]Both input and output files are of the same type (i.e. [bold].{file_type}[/bold]). No conversion necessary.[/yellow]')

    else:
        console.print('[red]ERROR: Invalid filenames.[/red]')
        console.print('[red]Try "ags4_cli convert --help" to see help and examples.[/red]')


if __name__ == '__main__':
    main()
