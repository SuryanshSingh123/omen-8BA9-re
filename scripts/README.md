# Before You Inspect:

## dump_ec.sh

As EC debug is available now (thanks to the modifications made in hp-wmi for debugging), capturing a dump is as simple as one command. However, (solely) for convenience, a executable is provided to neatly document the dump in a .txt file in the home directory.

Usage is simple, just execute this in your terminal (enter path)

## hp-wmi.c

Edits made by me will be marked as comments both at the beginning of the file and at the site of changes with descriptions for why a function was redefined/ other modifications.

## dump_diff.py
This is a small utility I wrote to compare two full EC dumps and present only the changed bytes in a readable format, since using diff in the terminal is a hassle.

It was primarily used to document the differences between:

- A fresh boot state (after rebooting from windows - see findings.md)
- The normal Linux "lazy fan" state after the EC settles

## dump_correlate.py
A utility to isolate which EC byte actually holds a given piece of state (e.g. thermal profile) across multiple dumps, filtering out noisy bytes like fan RPM or temperature counters that change on their own.

Take several dumps labeled by state (repeat a label to filter out jitter within that state):
```bash
python dump_correlate.py balanced=b1.txt balanced=b2.txt performance=p1.txt cool=c1.txt
```
It prints only the addresses that are stable within each label but differ across labels, i.e. candidates for the register you're looking for.

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
~/dump_ec.sh
# Wait or perform an action that changes EC state
~/dump_ec.sh
```
Finally, Compare them with the utility
```bash
python dump_diff.py ec_dump_1.txt ec_dump_2.txt
```
>Note: The exact build/install commands depend on how your kernel module is set up. The repository does not assume a specific DKMS or kernel build workflow.

# Big Tiny note
>These scripts are included for documentation and reproducibility rather than guaranteed functionality on current kernels, so don't expect everything to work as expected.