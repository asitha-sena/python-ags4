# python-ags4
A library to read and write AGS4 files using Pandas DataFrames

## Installation

```bash
pip install python-ags4
```

## Introduction
`python-ags4` is a library of functions that lets a user import [AGS4](http://www.agsdataformat.com/datatransferv4/intro.php) files to a collection of Pandas DataFrames. The data can be analyzed, manipulated, and updated using Pandas and then exported back to an AGS4 file.

## Examples

#### Import module:
```python
from python_ags4 import AGS4
```

#### Import data from an AG4 file:
```python
tables, headings = AGS4.AGS4_to_dataframe('/home/asitha/Projects/python-AGS4/tests/test_data.ags')
```
* *tables* is a dictionary of Pandas DataFrames. Each DataFrame contains the data from a *GROUP* in the AGS4 file. 
* *headings* is a dictionary of lists. Each list has the header names of the corresponding *GROUP*

All data are imported as text so they cannot be analyzed or plotted immediately. You can use the following code to convert all the numerical data in a DataFrame from text to numeric.

```python
LOCA = AGS4.convert_to_numeric(tables['LOCA'])
```

The `AGS4.convert_to_numeric()` function automatically converts all columns in the input DataFrame with the a numeric *TYPE* to a float. (*Note: The UNIT and TYPE rows are removed during this operation as they are non-numeric.*)

#### Export data back to an AGS4 file:

``` python
AGS4.dataframe_to_AGS4(tables, headings, '/home/asitha/Documents/output.ags')
```

A DataFrame with numeric columns may not get exported with the correct precision so they should be converted back to formatted text. The ```AGS4.convert_to_text()``` function will do this automatically if an AGS4 dictionary file is provided with the necessary UNIT and TYPE information. Numeric fields in the DataFrame that are not described in the dictionary file will be skipped with a warning.
```python
LOCA_txt = AGS4.convert_to_text(LOCA, 'DICT.ags')
```

Tables converted to numeric using the ```AGS4.convert_to_numeric()``` function should always be converted back to text before exporting to an AGS4 file. (*Note: The UNIT and TYPE rows will be added back in addition to formatting the numeric columns.*) 

## Graphical User Interface using *pandasgui*

The output from `python-ags4` can be directly used with [`pandasgui`](https://github.com/adamerose/pandasgui) to view and edit AGS4 files using an interactive graphical user interface. It also provides funtionality to plot and visualize the data.

```python
from pandasgui import show

tables, headings = AGS4.AGS4_to_dataframe('/home/asitha/Projects/python-AGS4/tests/test_data.ags')
gui = show(**tables)
```

<img src="https://github.com/asitha-sena/python-ags4/blob/master/tests/pandasgui_screenshot.PNG" width=800>

Any edits made in the GUI can be saved and exported back to an AGS4 file as follows:

*(Note: The code should be run before closing the GUI window)*

```python
updated_tables = gui.get_dataframes()

AGS4.dataframe_to_AGS4(updated_tables, headings, '/home/asitha/Documents/output.ags')
```
