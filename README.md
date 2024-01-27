![PyPI](https://img.shields.io/pypi/v/python-ags4?label=Current%20Release)
![PyPI - Downloads](https://img.shields.io/pypi/dm/python-ags4?label=Downloads%20pypi)
![Conda](https://img.shields.io/conda/dn/conda-forge/python-ags4?label=Downloads%20conda-forge)
[![DOI](https://joss.theoj.org/papers/10.21105/joss.04569/status.svg)](https://doi.org/10.21105/joss.04569)
![Tests](https://gitlab.com/ags-data-format-wg/ags-python-library/badges/main/pipeline.svg?ignore_skipped=true&key_text=Tests)

# python-ags4

[[_TOC_]]

## Introduction
`python-ags4` is a library of functions that

- imports/reads [AGS4](http://www.agsdataformat.com/datatransferv4/intro.php) files to a collection of [Pandas DataFrames](https://pandas.pydata.org/). 
- data can be analyzed, manipulated, and updated using Pandas 
- and then exported/written back to an AGS4 file

Release available at [pypi.org/project/python-ags4/](https://pypi.org/project/python-ags4/)

This project is maintained by the [AGS Data Format Working Group](https://gitlab.com/ags-data-format-wg) 

>>>
**Note**
 This repo was forked from [github.com/asitha-sena/python-ags4](https://github.com/asitha-sena/python-ags4) which is now archived and read-only
 
 HEAD is  [gitlab.com/ags-data-format-wg/ags-python-library](https://gitlab.com/ags-data-format-wg/ags-python-library)
>>>

## Documentation

### Installation

```bash
pip install python-ags4
```

>>>
**Note**
Installation requires Python 3.8 or later.
>>>

### Code Examples

First import the module.

```python
from python_ags4 import AGS4
```

#### Import data from an AGS4 file

```python
# Load from a file
tables, headings = AGS4.AGS4_to_dataframe('path/to/file.ags')

# Or use our sample data
from python_ags4.data import load_test_data
tables, headings = load_test_data()
```
* *tables* is a dictionary of Pandas DataFrames. Each DataFrame contains the data from a *GROUP* in the AGS4 file. 
* *headings* is a dictionary of lists. Each list has the header names of the corresponding *GROUP*

>>> 
**Important:** If the above code throws an exception or returns an empty dictionary, it very likely that the input file is not a valid AGS4 file. In such a case, the `AGS4.check_file()` function can be used to validate the file and see whether anything needs to be fixed before trying again. Most users will find it easier perform this step using the [command line interface](#command-line-interface) as it will provide a formatted error report that is much easier to read than the python dictionary created by directly calling the function.
>>>

All data are imported as text so they cannot be analyzed or plotted immediately. You can use the following code to convert all the numerical data in a DataFrame from text to numeric.

```python
LOCA = AGS4.convert_to_numeric(tables['LOCA'])
```

The `AGS4.convert_to_numeric()` function automatically converts all columns in the input DataFrame with the a numeric *TYPE* to a float. (*Note: The UNIT and TYPE rows are removed during this operation as they are non-numeric.*)

#### Export data back to an AGS4 file

``` python
AGS4.dataframe_to_AGS4(tables, headings, 'output.ags')
```

A DataFrame with numeric columns may not get exported with the correct precision so they should be converted back to formatted text. The ```AGS4.convert_to_text()``` function will do this automatically if an AGS4 dictionary file is provided with the necessary UNIT and TYPE information. Numeric fields in the DataFrame that are not described in the dictionary file will be skipped with a warning.
```python
LOCA_txt = AGS4.convert_to_text(LOCA, 'DICT.ags')
```

Tables converted to numeric using the ```AGS4.convert_to_numeric()``` function should always be converted back to text before exporting to an AGS4 file. (*Note: The UNIT and TYPE rows will be added back in addition to formatting the numeric columns.*) 

### Juypter Notebook

We have created an example Juypter Notebook which imports an AGS file, plots boreholes on a map and creates a Striplog.  

[See here](./notebooks/Plot_locations_and_create_strip_log.ipynb)

### Command Line Interface 

A cli tool was added in version 0.2.0. It should be available from the terminal (or on the Anaconda Powershell prompt in Windows) after running ```python pip install python-ags4>=0.2.0```

It does not yet have the full functionality of the library, but it does provide a quick and easy way to convert .ags files to Excel spreadsheets (.xlsx) and back. The data can be easily edited in a spreadsheet and then converted back a .ags file. The TYPE values for numeric columns can be changed in the spreadsheet and the data will be automatically reformatted correctly when converted back to .ags, as long as all values in a column are numbers. Any supposedly numeric columns with text entries will be skipped with a warning message.

*(Note: All data is imported to the spreadsheet as text entries so any column that should be reformatted should be explicitly converted to numbers in Excel.)*

[![asciicast](https://asciinema.org/a/O7zhgGqWlobK8Hiyqrx3NGtaf.svg)](https://asciinema.org/a/O7zhgGqWlobK8Hiyqrx3NGtaf)

A checking tool is available as of version 0.3.0 and it can be used to make sure that the file conforms to the AGS4 rules. The tool has been tested in both bash and Powershell.

[![asciicast](https://asciinema.org/a/OOVN1rtqpvggzt9ZlHAlLBb6M.svg)](https://asciinema.org/a/OOVN1rtqpvggzt9ZlHAlLBb6M)

### Graphical User Interface using *pandasgui*

The output from `python-ags4` can be directly used with [`pandasgui`](https://github.com/adamerose/pandasgui) to view and edit AGS4 files using an interactive graphical user interface. It also provides funtionality to plot and visualize the data.

```python
from pandasgui import show
from python_ags4.data import load_test_data

tables, headings = load_test_data()
gui = show(**tables)
```

<img src="./docs/media/pandasgui_screenshot.png" width=800>

Any edits made in the GUI can be saved and exported back to an AGS4 file as follows:

```python
updated_tables = gui.get_dataframes()

AGS4.dataframe_to_AGS4(updated_tables, headings, 'output.ags')
```

### Development

Please refer to the [Wiki](https://gitlab.com/ags-data-format-wg/ags-python-library/-/wikis/home) page for details about the development environment and how to get involved in the project.

API documentation available at https://ags-data-format-wg.gitlab.io/ags-python-library

### Citation

Senanayake et al., (2022). python-ags4: A Python library to read, write, and validate AGS4 geodata files. Journal of Open Source Software, 7(79), 4569, https://doi.org/10.21105/joss.04569

## Implementations

This library has been used to create

- Windows Desktop Application - https://gitlab.com/ags-data-format-wg/ags-checker-desktop-app 
- Web application and API (pyagsapi) - https://github.com/BritishGeologicalSurvey/pyagsapi 
  - Deployed as https://agsapi.bgs.ac.uk/
- Excel Add On - https://gitlab.com/RogerChandler/ags-validator-excel-add-in  
