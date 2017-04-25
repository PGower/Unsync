# Unsync
A data extraction / transformation and loading tool written in python using the Click and PETL libraries.

This tool was created to try and ease the development of automated processes that could take data from one or more external systems, perform some processing and then send that data to one or more places.
While this problem could be tackled in pure python I found that this produced code that was fairly specific to the issue at hand and did not allow itself to be easily modified. What I wanted was a way to easily define these data flows from reusable blocks and to be able to modify them easily when my requirements changed.

The solution I settled on was the Unsync tool. The tool uses the PETL library to perform the actual data processing work and the Click library to wrap the whole thing in a command line interface. Using chained click commands a process can be quickly built up from the individual subcommands in a shell script. Individual commands are completely isolated from each other which makes modifying the chain easy.

This tool is still at an alpha stage and parts of the architecture are still changing based on my own experience using it.
