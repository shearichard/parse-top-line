# ptl : Parse Top Line

Parses output of the top utility when top has been run in batch mode to produce a more usable output.

As it currently exists this project is very specic to my needs which centre upon comparing the memory usage of two different modes of running an executable. In one mode the executable is asked to all the processing necessary in one go, in the second mode things are arranged so that the executable is asked to run three times and each time part of the necessary processing is completed. It's unlikely these are your requirements but perhaps this project might help you if you have related needs.

## configconstants File

The `ptl.py` module is dependent upon a module `configconstants.py` which is not saved in the repository.

The structure of that module is as follows and you may add whatever data is relevant to your needs.

```
DIRDATA='''../data/dirwithoutputin/'''
TOPLOGBASELINE='''top-output-baseline.log'''
TOPLOGSERIAL='''top-output-serial.log'''
```
