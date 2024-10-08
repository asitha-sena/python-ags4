# Usage
## Introduction
`python-ags4` is a library of functions that

- imports/reads [AGS4](http://www.agsdataformat.com/datatransferv4/intro.php) files to a collection of [Pandas DataFrames](https://pandas.pydata.org/). 
- data can be analyzed, manipulated, and updated using Pandas 
- and then exported/written back to an AGS4 file

Release available at [pypi.org/project/python-ags4/](https://pypi.org/project/python-ags4/)

This project is maintained by the [AGS Data Format Working Group](https://gitlab.com/ags-data-format-wg) 


!!! note

    This repo was forked from [github.com/asitha-sena/python-ags4](https://github.com/asitha-sena/python-ags4) which is now archived    and read-only
 
    HEAD is  [gitlab.com/ags-data-format-wg/ags-python-library](https://gitlab.com/ags-data-format-wg/ags-python-library)


## Documentation

### Installation

```bash
pip install python-ags4
```

!!! note

    Installation requires Python 3.9 or later.


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


!!! warning

    If the above code throws an exception or returns an empty dictionary, it very likely that the input file is not a valid AGS4 file. In such a case, the `AGS4.check_file()` function can be used to validate the file and see whether anything needs to be fixed before trying again. Most users will find it easier to perform this step using the [command line interface](#command-line-interface) as it will provide a formatted error report that is much easier to read than the python dictionary created by directly calling the function.


All data are imported as text so they cannot be analyzed or plotted immediately. You can use the following code to convert all the numerical data in a DataFrame from text to numeric.

```python
LOCA = AGS4.convert_to_numeric(tables['LOCA'])
```

The `AGS4.convert_to_numeric()` function automatically converts all columns in the input DataFrame with a numeric *TYPE* to a float. (*Note: The UNIT and TYPE rows are removed during this operation as they are non-numeric.*)

#### Export data back to an AGS4 file

``` python
AGS4.dataframe_to_AGS4(tables, headings, 'output.ags')
```

A DataFrame with numeric columns may not get exported with the correct precision so they should be converted back to formatted text. The ```AGS4.convert_to_text()``` function will do this automatically if an AGS4 dictionary file is provided with the necessary UNIT and TYPE information. Numeric fields in the DataFrame that are not described in the dictionary file will be skipped with a warning.
```python
LOCA_txt = AGS4.convert_to_text(LOCA, 'DICT.ags')
```

Tables converted to numeric using the ```AGS4.convert_to_numeric()``` function should always be converted back to text before exporting to an AGS4 file. (*Note: The UNIT and TYPE rows will be added back in addition to formatting the numeric columns.*) 

### Jupyter Notebook

We have created an example Jupyter Notebook which imports an AGS file, plots boreholes on a map and creates a Striplog.

[See here](./notebooks/Plot_locations_and_create_strip_log.ipynb)

### Command Line Interface

A command-line interface (CLI) to access the core functionality of the library
is available since version 0.2.0. It is automatically installed together with the
library and can be accessed by typing ```ags4_cli``` in a terminal/shell. If you
want the CLI to be available globally (i.e. not limited to a single virtual
environment), then you can install it using ```pipx```.

You can do the following operations via the CLI:
1. Check/validate AGS4 files
  [![asciicast](https://asciinema.org/a/tROg0S28hPmcyYsUrkuAgWoAB.svg)](https://asciinema.org/a/tROg0S28hPmcyYsUrkuAgWoAB)

2. Convert AGS4 to Excel spreadsheets (.xlsx) and back
  [![asciicast](https://asciinema.org/a/O7zhgGqWlobK8Hiyqrx3NGtaf.svg)](https://asciinema.org/a/O7zhgGqWlobK8Hiyqrx3NGtaf)
  The data can be easily edited in a spreadsheet and then converted back a .ags
  file. The TYPE values for numeric columns can be changed in the spreadsheet
  and the data will be automatically reformatted correctly when converted back
  to .ags, as long as all values in a column are numbers. Any supposedly numeric
  columns with text entries will be skipped with a warning message. *(Note: All
  data is imported to the spreadsheet as text entries so any column that should
  be reformatted should be explicitly converted to numbers in Excel.)*
  
3. Sort groups/tables in AGS4 files
  [![asciicast](https://asciinema.org/a/fEMPXSGGssXy2eoYbUiKFoW8b.svg)](https://asciinema.org/a/fEMPXSGGssXy2eoYbUiKFoW8b)


### Graphical User Interface using *pandasgui*

The output from `python-ags4` can be directly used with [`pandasgui`](https://github.com/adamerose/pandasgui) to view and edit AGS4 files using an interactive graphical user interface. It also provides functionality to plot and visualize the data.

```python
from pandasgui import show
from python_ags4.data import load_test_data

tables, headings = load_test_data()
gui = show(**tables)
```

<img src="./media/pandasgui_screenshot.png" width=800>

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
