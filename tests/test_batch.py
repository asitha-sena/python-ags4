
import os
import json
import filecmp
import glob

from python_ags4 import AGS4


def checkandcompare(AGSFilename):
    ErrorFilename = AGSFilename.replace(".ags", ".errors")
    CheckFilename = AGSFilename.replace(".ags", ".check")

    try:
        error_list = AGS4.check_file(AGSFilename, standard_AGS4_dictionary='python_ags4/Standard_dictionary_v4_1.ags')

        # remove Metadata item it is exists as this will change everytime it is checked
        if "Metadata" in error_list.keys():
            error_list.pop("Metadata")

        f = open(ErrorFilename, "w")
        app_json = json.dumps(error_list)
        f.write(app_json)
        f.close()

    except AGS4.AGS4Error as err:
        f = open(ErrorFilename, "w")
        f.write(str(err))
        f.close()

    finally:
        if glob.glob(CheckFilename):
            if filecmp.cmp(ErrorFilename, CheckFilename, shallow=False):
                os.remove(ErrorFilename)  # remove the error file as this is no longer required
                return 'Passed - ' + AGSFilename
            else:
                return 'Failed - ' + AGSFilename + ' - errors different from file'
        else:
            return 'Failed - ' + AGSFilename + ' - no file to check against'


# Routine to check all the AGS files within the Test_files directory and compare the results against a known output file
# the check files (.check) can be created as a copy of the .errors file once the error output has been manually checked and validated.


AGSDirectory = "tests/test_files/"


LogFilename = "tests/batchlog.txt"
f = open(LogFilename, "w")

# Find all AGS files
files = glob.glob(AGSDirectory + '**/*.ags', recursive=True)
for AGSFilename in files:
    # Check the file and compare it
    test = checkandcompare(AGSFilename)
    # write results to the log file
    f.write(test + "\n")

f.close()
print(LogFilename + " written")
