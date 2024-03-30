## Welcome to python_ags4 official documentation

[![image](https://img.shields.io/pypi/v/python-ags4?label=Current%20Release)](https://pypi.org/project/python-ags4) ![image](https://img.shields.io/pypi/dm/python-ags4?label=Downloads%20pypi) ![image](https://img.shields.io/conda/dn/conda-forge/python-ags4?color=green&label=Downloads%20conda-forge)

[![image](https://joss.theoj.org/papers/10.21105/joss.04569/status.svg)](https://doi.org/10.21105/joss.04569) [![image](https://gitlab.com/ags-data-format-wg/ags-python-library/badges/main/pipeline.svg?ignore_skipped=true&key_text=Tests)](https://gitlab.com/ags-data-format-wg/ags-python-library)

**python-ags4** is a library of functions that:

-   imports/reads
    [AGS4](http://www.agsdataformat.com/datatransferv4/intro.php) files
    to a collection of [Pandas DataFrames](https://pandas.pydata.org/).
-   data can be analyzed, manipulated, and updated using Pandas
-   and then exported/written back to an AGS4 file

Release available at [PyPI](https://pypi.org/project/python-ags4)

This project is maintained by the [AGS Data Format Working
Group](https://gitlab.com/ags-data-format-wg)


-   LICENSE: [GNU LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html)

**modules inluded**

 - AGS4.py
 - check.py
 - ags_cli.py

## Project Scope
For many years the industry has had two checker applications that don't always produce the same results.  This has caused clients to specify that AGS files must pass both checkers before the data is submitted to them, resulting in additional work for clients, contractors and software producers.

The Project has one goal.  To produce an AGS Validator library that can be used by any developer to include AGS validation routine in their application.  By Producing a single code stream that can be incorporated into any application the industry will now know if a file is valid.

The project has also created an EXE file with a simple interface that allows users to validate files.  More information on this project can be found in the Related Projects section of this Wiki.  This library will not visualize or fix AGS data but we welcome developers to start their own related project.


## Release Notes
May 4th 2021 - AGS Validator EXE Beta launched
This release is for testing by the development team and the AGS committee members.  We believe that it finds all the errors in AGS 4.0.3, 4.0.4 and 4.1 files with the known issue list below. 

Line numbers are not included in all error messages

## Adding Test AGS Files
The project has launched with 55 AGS files that have deliberate errors in them. Each file has a corresponding .check file with it that defines the errors that are in the file.

Every AGS file in the /tests/test_files folder is checked before a release is made to ensure that any modifications don't break any checks or introduce new problems.

If you have an AGS file where the validator either incorrectly identifies an error or does not highlight a known error then we would like to know about it so we can fix any problems and include this file in the checking routine.

To report problems please open an issue, describe the error and attach the file. The Contributor Team will then review the file, create the .check file and include it in the main Repository.

## Credits
The AGS Python Library is created and maintained by a range of enthusiastic international volunteers (like you)

Beta Release 0.0.1 4th May 2021

The initial beta release was made possible due to the considerable work completed by Asitha Senanayake with support and testing by Roger Chandler and Tony Daly.

We welcome push requests from any AGS developer within the bounds of the project, so get coding and create a push request to join the contribution team and see your name add to this Credits Page for the next release.

## Development Environment
This project is built in Ubuntu 20.04 and packaged using `poetry` (python-poetry.org). Unit testing is done using `pytest` with the `toml` library as a dependency.

Instructions on how to install `poetry` can be found at https://python-poetry.org/docs/.
This package does not come with _setup.py_ and _requirements.txt_ files. Instead, all dependency information is provided in the _pyproject.toml_ and _poetry.lock_ files.

A development environment can be setup by running `poetry install` from within the root directory of the git repo. It will install all packages listed in the _poetry.lock_ file and also install `python_ags4` in editable mode. (Running `pip install -e` to install the package in editable mode does not work because there is no _setup.py_ file.)

If you want only the dependencies installed, then run `poetry install --no-root` instead.
Unit tests can be run by running `python -m pytest` from within the root directory of the git repo.

Dev directory is structured as shown below:

![dev_directory_structure](uploads/0ec81e34b20fea36995dcc9342720181/dev_directory_structure.png)

## Get Involved
If you are reading this then you are already involved! Thank you for being part of this amazing project. If you share our passion for this project and would like to be involved then we are looking for people to help in any of the roles below. Just introduce yourself to the team via

Users (Primary role is to ensure the requirements are defined and met)
Developer (Primary role is to develop code against the requirements)
Managers (Primary role is to merge pull requests from contributors)
Controllers (Primary role is governance and PR)

## Related Projects
The AGS library is an excellent tool for any developers to add AGS validation capabilities to their application but is not user friendly for users.<br><br>
To help users validate AGS files using this library the following tools should be reviewed.  Please see the links below for the status of each of these projects.<br><br> 
- [AGS Validator EXE](https://gitlab.com/ags-data-format-wg/ags-checker-desktop-app) (Released by AGS)
- [AGS Excel Add-In](https://gitlab.com/RogerChandler/ags-validator-excel-add-in) (Developed by Roger Chandler)
- [AGS Validator Web Interface and API](https://github.com/BritishGeologicalSurvey/AGS-Validator-FastAPI-Web-App ) (Developed by BGS)


Use the navigation menu on the left and the search to find what you want.


