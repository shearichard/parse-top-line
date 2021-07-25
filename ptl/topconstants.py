# Comments on following constants are derived from
# https://man7.org/linux/man-pages/man1/top.1.html
#
PID=0 # Process Id 
USER=1 # The effective user name of the task's owner
PR=2 # The scheduling priority of the task (some caveats apply on linux)
NI=3 # Nice Value
VIRT=4 # The total amount of virtual memory used by the task.  It includes all code, data and shared libraries plus pages that have been swapped out and pages that have been mapped but not used.
RES=5 # Resident Memory Size (KiB) (Some subtlety here, need to refer to doco)
SHR=6 # Shared Memory Size (KiB)
S=7 # Process Status 
PERC_CPU=8 # The task's share of the elapsed CPU time since the last screen update, expressed as a percentage of total CPU time.
PERC_MEM=9 # A task's currently resident share of available physical memory.
TIME=10 # CPU Time - Total CPU time the task has used since it started 
COMMAND=11 # Command line used to start a task
