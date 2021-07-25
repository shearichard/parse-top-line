'''
ptl.py

Parse a log like that shown below and output a  dictionary keyed by pid 
(the zero column) and within that another dictionary keyed by row index. 

The data should be the value shown here in column 4 (which contains the 
memory usage) and process name (column 11).

Bear in mind some rows have 'human-friendly' memory values (such as 23.1g)
and so need to be translated back to raw numbers.

Here's a sample of the file:

  19159 www-data  20   0    3740   2760   2540 S   0.0   0.0   0:00.00 foon
  19165 www-data  20   0    3740   2252   1984 S   0.0   0.0   0:00.00 foon
  19166 www-data  20   0   22664   6464   6256 D   0.0   0.0   0:00.00 foodb_path
  19168 www-data  20   0 6562276  65916  62492 S   8.7   0.1   0:00.09 foon.REAL
  19159 www-data  20   0    3740   2880   2612 S   0.0   0.0   0:00.00 foon
  19168 www-data  20   0 6562276 106116  92232 S  58.4   0.2   0:00.68 foon.REAL
  19159 www-data  20   0    3740   2880   2612 S   0.0   0.0   0:00.00 foon
'''
import json
import re
import os
from pathlib import Path
import csv
from decimal import *
import math
import tempfile


import configconstants
from topconstants import *

RGXSTR = r"""(\d+(?:\.\d+)?)(.*)"""
dicproblems = {}
dicmultiplers = {'g': 1024*1024, 'm':1024}


def dehumanise_size(sz, rgx_compile_obj):
    '''
    Take values such as '23.1g' and turn it into plain numbers
    '''
    try:
        szout = int(sz)
    except ValueError:
        match_obj = rgx_compile_obj.search(sz)
        numeric_component = match_obj.group(1)
        unit_component = match_obj.group(2)
        #
        if unit_component in dicmultiplers:
            szout = math.floor(Decimal(numeric_component) * dicmultiplers[unit_component])
        else:
            raise ValueError(f"Unknown unit used when trying to convert {sz} to humanized version")
    except:
        raise

    return szout

def parsetoplog(pathtotoplog):
    '''
    Read through the log file and generate a multi-level dictionary.

    The top level is keyed on PID id and maps to a dictionary. The
    mapped dictionary is keyed by row number and contains a subset
    of all the values in the corresponding row.
    '''

    dicout = {}
    idx=0
    rgx_compile_obj = re.compile(RGXSTR)
    #
    if pathtotoplog.is_file():
        pass
    else:
        raise ValueError(f"Input file, {pathtotoplog} does not exist")
    #
    csv.register_dialect('skip_space', skipinitialspace=True)
    with open(pathtotoplog, 'r') as f:
        reader=csv.reader(f , delimiter=' ', dialect='skip_space')
        for topoutput in reader: 
            if topoutput[PID] not in dicout:
                dicout[topoutput[PID]] = {}
            #
            if idx in dicout[topoutput[PID]]:
                raise ValueError('There should never be duplicate key derived from idx')
            else:
                try:
                    virt = dehumanise_size(topoutput[VIRT], rgx_compile_obj)
                    res = dehumanise_size(topoutput[RES], rgx_compile_obj)
                    shr = dehumanise_size(topoutput[SHR], rgx_compile_obj)
                    pr = dehumanise_size(topoutput[PR], rgx_compile_obj)
                except:
                    print(topoutput)
                    raise
                #
                dicout[topoutput[PID]][idx] = { 'VIRT': topoutput[VIRT],
                                                'RES': res, 
                                                'SHR': shr,
                                                'PR':  pr,
                                                'RES_READABLE': "{:,}".format(res),
                                                'SHR_READABLE': "{:,}".format(shr),
                                                'PR_READABLE': "{:,}".format(pr),
                                                'S':  topoutput[S],
                                                'PERC_MEM':  topoutput[PERC_MEM]
                                                } 
            #
            idx+=1

    return dicout


def dump_json_to_tmp(dic_in):
    '''
    Take a dictionary and dump it to a JSON file
    in a temporary directory. Return the path
    of the JSON file.
    '''
    
    output_dir=tempfile.mkdtemp(prefix='ptl_output_')
    output_path = os.path.join(output_dir, 'ptl.json')
    with open(output_path, 'a') as fp:
        json.dump(dic_in, fp)
    return output_path


def main():
    dic_bl_analysis = parsetoplog(Path(os.path.join(configconstants.DIRDATA,configconstants.TOPLOGBASELINE)))
    path_to_output = dump_json_to_tmp(dic_bl_analysis)
    print(path_to_output)


if __name__ == "__main__":
    main()
