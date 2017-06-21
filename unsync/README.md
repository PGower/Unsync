# Unsync
A data extraction / transformation and loading tool written in python using the Click and PETL libraries.

This tool was created to try and ease the development of automated processes that could take data from one or more external systems, perform some processing and then send that data to one or more places.
While this problem could be tackled in pure python I found that this produced code that was fairly specific to the issue at hand and did not allow itself to be easily modified. What I wanted was a way to easily define these data flows from reusable blocks and to be able to modify them easily when my requirements changed.

The solution I settled on was the Unsync tool. The tool uses the PETL library to perform the actual data processing work and the Click library to wrap the whole thing in a command line interface. Using chained click commands a process can be quickly built up from the individual subcommands in a shell script. Individual commands are completely isolated from each other which makes modifying the chain easy.

This tool is still at an alpha stage and parts of the architecture are still changing based on my own experience using it.

## Current Directions
In the short term there are 3 things that I think need to happen.
1. The tool needs to be modularised further and commands need to be loaded from python packages.
   Currently the dependenices for the package are getting a bit heavy and modularising sets of commands into packages would help to fix this issue.
   It should also make it easier for someone to write a custom set of commands and then publish them for use in the tool.
2. I need to better define where Click ends and Unsync starts. The three major parts of the Click library that I am using have all been subclassed (Command, Data, Option).
   It should be possible to create an Unsync command and not have to import anything except for the unsync library.
3. Although this tool was originally intended to be scheduled to run it does not do a good job of reporting errors. I need to create more options to catch and report errors in useful ways (email, syslog?)

## Usage Example
Once installed from pip:
` pip install unsync
The unsync command should be available on your path. You can either use it directly from the command line or for longer processing tasks you can incorporate it into a shell (batch) script.
An example of such a script in windows batch might be:
    unsync.exe --debug ^
    csv_import -i source\user_names.csv --destination user_names ^
    petl_select --source user_names --selector "{first_name}.startswith('d')" ^
    csv_export --source user_names -o filtered_user_names.csv
There are many more commands which can be used to manipulate the data and ''

