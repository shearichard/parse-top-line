'''
ptl.py

Parse a log like that shown below and output a  dictionary keyed by pid 
(the zero column) and within that another dictionary keyed by row index. 

The data should be the value shown here in column 4 (which contains the 
memory usage) and process name (column 11).

Bear in mind some rows have 'human-friendly' memory values (such as 23.1g)
and so need to be translated back to raw numbers.

Here's the same of the file:

  19159 www-data  20   0    3740   2760   2540 S   0.0   0.0   0:00.00 foon
  19165 www-data  20   0    3740   2252   1984 S   0.0   0.0   0:00.00 foon
  19166 www-data  20   0   22664   6464   6256 D   0.0   0.0   0:00.00 foodb_path
  19168 www-data  20   0 6562276  65916  62492 S   8.7   0.1   0:00.09 foon.REAL
  19159 www-data  20   0    3740   2880   2612 S   0.0   0.0   0:00.00 foon
  19168 www-data  20   0 6562276 106116  92232 S  58.4   0.2   0:00.68 foon.REAL
  19159 www-data  20   0    3740   2880   2612 S   0.0   0.0   0:00.00 foon
'''
import os
from pathlib import Path
import csv

import configconstants
from topconstants import *




def parsetoplog(pathtotoplog):
    dicout = {}
    filestatus="does not exist."

    if pathtotoplog.is_file():
        filestatus="does exist."

    print(f'''{pathtotoplog} {filestatus}''')

    csv.register_dialect('skip_space', skipinitialspace=True)
    idx=0
    with open(pathtotoplog, 'r') as f:
        reader=csv.reader(f , delimiter=' ', dialect='skip_space')
        for topoutput in reader:
            if topoutput[PID] not in dicout:
                dicout[topoutput[PID]] = {}
            #
            if idx in dicout[topoutput[PID]]:
                raise ValueError('There should never be duplicate key derived from idx')
            else:
                dicout[topoutput[PID]][idx] = { 'VIRT': topoutput[VIRT],
                                                'RES': topoutput[RES], 
                                                'SHR': topoutput[SHR],
                                                'PR':  topoutput[PR],
                                                'S':  topoutput[S],
                                                'PERC_MEM':  topoutput[PERC_MEM]
                                                } 
            #
            idx+=1
            if idx > 5:
                break

        import pprint
        pprint.pprint(dicout)


def main():
    dic_bl_analysis = parsetoplog(Path(os.path.join(configconstants.DIRDATA,configconstants.TOPLOGBASELINE)))

if __name__ == "__main__":
    main()
