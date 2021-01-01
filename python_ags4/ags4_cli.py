#!/usr/bin/env python

import click
from python_ags4 import AGS4
from rich.console import Console

# Create rich console for pretty printing
console = Console()


@click.group()
def main():
    '''Tool to read and edit AGS4 files.
    '''
    pass


@main.command()
@click.argument('input_file')
@click.argument('output_file')
def convert(input_file, output_file):
    '''Convert .ags file to .xlsx file
    '''

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

        AGS4.excel_to_AGS4(input_file, output_file)

        console.print('\n[green]File conversion complete! :heavy_check_mark:[/green]\n')

    else:
        print('Invalid input. Please check filenames...')


if __name__ == '__main__':
    main()
