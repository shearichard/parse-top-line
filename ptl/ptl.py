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
import sys
import json
import re
import os
from pathlib import Path
import csv
from decimal import *
import math
import tempfile
import pprint


import configconstants
from topconstants import *

RGXSTR = r"""(\d+(?:\.\d+)?)(.*)"""
dicproblems = {}
dicmultiplers = {'g': 1024*1024*1024, 'm':1024*1024}


def dehumanise_size(sz, rgx_compile_obj):
    '''
    Take values such as '23.1g' and turn it into plain numbers
    '''
    if sz == "":
        szout = -1
    else:
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
            if len(topoutput) != 12:
                print("Skipping this line ...")
                print(topoutput)
            else:
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
                    dicout[topoutput[PID]][idx] = { 'VIRT': virt,
                                                    'RES': res, 
                                                    'SHR': shr,
                                                    'PR':  pr,
                                                    'VIRT_READABLE': "{:,}".format(virt),
                                                    'RES_READABLE': "{:,}".format(res),
                                                    'SHR_READABLE': "{:,}".format(shr),
                                                    'PR_READABLE': "{:,}".format(pr),
                                                    'S':  topoutput[S],
                                                    'PERC_MEM':  float(topoutput[PERC_MEM])
                                                    } 
            #
            idx+=1

    return dicout


def analyse_json_for_stats(dic_bl_analysis):
    tl_keys = dic_bl_analysis.keys()
    print(f'''Number of PIDs : {len(tl_keys)} .''')
    #
    for pk in tl_keys:
        dic_status = make_empty_status_dic()
        virt_min = sys.maxsize * 2 + 1 
        virt_max = 0
        perc_mem_min = sys.maxsize * 2 + 1 
        perc_mem_max = 0
        for _ , tld in dic_bl_analysis[pk].items():
            #import pdb;pdb.set_trace()
            if tld['S'] not in dic_status:
                dic_status[tld['S']] = 1
            else:
                dic_status[tld['S']] += 1
            #
            if Decimal(tld['VIRT']) < virt_min:
                virt_min = tld['VIRT']
            if Decimal(tld['VIRT']) > virt_max:
                virt_max = tld['VIRT']
            if Decimal(tld['PERC_MEM']) < perc_mem_min:
                perc_mem_min = tld['PERC_MEM']
            if Decimal(tld['PERC_MEM']) > perc_mem_max:
                perc_mem_max = tld['PERC_MEM']

        duration_tuple = divmod(len(dic_bl_analysis[pk].keys()), 60)
        print(f'''Log entries for {pk}: {len(dic_bl_analysis[pk].keys())} (Therefore, probably {duration_tuple[0]}:{duration_tuple[1]:02}). Virt in range {"{:,}".format(virt_min)} to {"{:,}".format(virt_max)}. %_MEM in range {perc_mem_min} to {perc_mem_max}.''')
        pprint.pprint(dic_status)
        print("")


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


def make_job_list():
    return [{'desc':'baseline', 'infile':configconstants.TOPLOGBASELINE}, {'desc':'serial', 'infile':configconstants.TOPLOGSERIAL}]

def make_empty_status_dic():

    dicout={}
    dicout['D'] = 0 
    dicout['I'] = 0 
    dicout['R'] = 0 
    dicout['S'] = 0 
    dicout['T'] = 0 
    dicout['t'] = 0 
    dicout['Z'] = 0 
    return dicout

def main():
    for job in make_job_list():
        print(f'''Processing {job['desc']}''')
        dic_bl_analysis = parsetoplog(Path(os.path.join(configconstants.DIRDATA, job['infile'])))
        path_to_output = dump_json_to_tmp(dic_bl_analysis)
        dic_stats = analyse_json_for_stats(dic_bl_analysis)
        print(path_to_output)
        print("")


if __name__ == "__main__":
    main()
