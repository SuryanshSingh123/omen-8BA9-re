# Before You Inspect

The EC scripts are provided primarily to document the workflow used during this investigation. They automate the process of dumping and comparing Embedded Controller (EC) bytes and are intended as references for reproducing the experiments

On newer kernels (7.1+), these scripts will most likely **not** function because the EC debug interface (`/sys/kernel/debug/ec/ec0/io`) is unavailable due to the absence of the `ec_sys`/`CONFIG_ACPI_EC_DEBUGFS` interface at runtime

If EC debug access becomes available in the future, the scripts can be used without any modification (hopefully)

# hp-wmi.c

Edits made by me will be marked as comments both at the beginning of the file and at the site of changes with descriptions for why a function was redefined/ other modifications.


### Tiny note:
>These scripts are included for documentation and reproducibility rather than guaranteed functionality on current kernels.