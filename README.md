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

The `AGS4.convert_to_numeric()` function automatically converts all columns in the input DataFrame with the a numeric *TYPE* to a float.

#### Export data back to an AGS4 file:

``` python
AGS4.dataframe_to_AGS4(tables, headings, '/home/asitha/Documents/output.ags')
```
