## Editing the hp-wmi.c file 

The file used by the service did not contain my motherboad's ID(8BA9) in both "omen_thermal_profile_boards" and "omen_timed_thermal_profile_boards"

A very odd observation, since its' sibling boards/the ones released fairly close in time (8A15, 8A42, and 8BAD) were in fact included in the C file(provided in scripts folder of this repo).
I tried to simply include my motherboard's ID in the given value list and reload hp-wmi.
It did not work, of course this wasn't going to be a simple 'add a line patch'.