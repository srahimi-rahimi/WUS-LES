qstat -fx "$PBS_JOBID" | grep -Ei \
    "Exit_status|resources_used.mem|resources_used.vmem|resources_used.walltime|comment"
