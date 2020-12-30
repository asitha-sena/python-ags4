#!/usr/bin/env python

import click
from python_ags4 import AGS4


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
        print(f'Opening file... {input_file}')
        print(f'Exporting data to... {output_file}')

        AGS4.AGS4_to_excel(input_file, output_file)

    elif input_file.endswith('.xlsx') & output_file.endswith('.ags'):
        print(f'Opening file... {input_file}')
        print(f'Exporting data to... {output_file}')

        AGS4.excel_to_AGS4(input_file, output_file)

    else:
        print('Invalid input. Please check filenames...')


if __name__ == '__main__':
    main()
