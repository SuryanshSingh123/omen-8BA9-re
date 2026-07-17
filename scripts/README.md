# Before You Inspect:

## Shell scripts

The EC scripts are provided primarily to document the workflow used during this investigation. They automate the process of dumping and comparing Embedded Controller (EC) bytes and are intended as references for reproducing the experiments

On newer kernels (7.1+), these scripts will most likely **not** function because the EC debug interface (`/sys/kernel/debug/ec/ec0/io`) is unavailable due to the absence of the `ec_sys`/`CONFIG_ACPI_EC_DEBUGFS` interface at runtime

If EC debug access becomes available in the future, the scripts can be used without any modification (hopefully)

## hp-wmi.c

Edits made by me will be marked as comments both at the beginning of the file and at the site of changes with descriptions for why a function was redefined/ other modifications.

## dump_diff.py
This is a small utility I wrote to compare two full EC dumps and present only the changed bytes in a readable format, since using diff in the terminal is a hassle.

It was primarily used to document the differences between:

- A fresh boot state (after rebooting from windows - see findings.md)
- The normal Linux "lazy fan" state after the EC settles

### Usage
First, replace your system's hp-wmi.c with the modified version provided in /scripts/hp-wmi.c (or implement an equivalent EC dump function yourself).

Place dump_diff.py somewhere convenient (such as your home directory)

Rebuild and reinstall the hp-wmi module using your preferred method (DKMS, manual kernel module build, etc.), then reload it:
``` bash
sudo modprobe -r hp_wmi
sudo modprobe hp_wmi
```
And capture two EC dumps:
```bash
sudo dmesg -w | grep -A260 "Full EC dump" > 1_ec_dump.txt
# Wait or perform an action that changes EC state
sudo dmesg -w | grep -A260 "Full EC dump" > 2_ec_dump.txt
```
Finally, Compare them with the utility
```bash
python dump_diff.py 1_ec_dump.txt 2_ec_dump.txt
```
>Note: The exact build/install commands depend on how your kernel module is set up. The repository does not assume a specific DKMS or kernel build workflow.

# Big Tiny note
>These scripts are included for documentation and reproducibility rather than guaranteed functionality on current kernels, so don't expect everything to work as expected.