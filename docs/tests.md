## Editing the hp-wmi.c file

The driver source did not contain my motherboard ID (`8BA9`) in either
`omen_thermal_profile_boards` or
`omen_timed_thermal_profile_boards`. (it does later in the 7.1+ update)

A notable observation is that several closely related boards (8A15, 8A42,
8BAD) are already listed.

As an experiment, I manually added `8BA9` to both board lists, rebuilt the
DKMS module, and reloaded `hp_wmi`.

### Result

The driver loaded successfully, but:

- fan RPMs remained 0
- platform profile still failed to initialize
- no additional fan functionality became available

### Conclusion

Board detection is only one part of the initialization path.
Simply adding the motherboard ID was surely not going to enable support for this
model.

## Kernel update

### Purpose

Determine whether the failures were caused by a kernel / module mismatch.

### Result

Updated from:

7.1.3-arch1-3

to

7.1.3-arch2-1

The DKMS module now builds and loads correctly.

The previous error

hp_wmi: query 0x4c returned error 0x6

changed to

Failed to read current platform profile (-22)

### Conclusion

The original kernel mismatch prevented proper loading of the DKMS module.

After correcting the kernel mismatch, the driver proceeds further into
initialization before failing, indicating that the remaining issue is inside
the driver's interaction with this specific laptop rather than module loading.

## EC Read Investigation

Verified that hp-wmi ultimately calls Linux ACPI EC helpers (`ec_read()`) rather than directly accessing debugfs.

Flow:

```
platform_profile_omen_get_ec()
        ↓
omen_thermal_profile_get()
        ↓
ec_read(0x95, &data)
        ↓
switch(data)
```
Current failure occurs because the returned value is not one of the expected
thermal profile constants, causing the driver to return -EINVAL.

## Embedded Controller

- EC register `0x95` is readable through `ec_read()`
- `ec_read()` succeeds (`ret = 0`)
- The EC returns value `0x43`
- `hp_wmi` currently recognizes only:
  - `0x00`
  - `0x01`
  - `0x02`
  - `0x30`
  - `0x31`
  - `0x50`
- Since `0x43` is not recognized, the driver returns `-EINVAL`, producing:
  - `Failed to read current platform profile (-22)`

## RWEverything

Used specialized read and write tool to investigate the EC in real time, while switching profiles in Windows and looking at the live register.

### Result

- One noticeable byte everytime I switched profiles (could see it with bare eyes)
- Successfully found profile register, Register 89

### Conclusion

- Register 89 has 30 at balanced and 31 at performance. This is literally the syntax for V1 boards mentioned in the C file.
- Therefore, the driver needed to read 0x59 for this board, not 0x95.

>It's kinda funny because 59 is 95 with reversed digits. Reverse engineering joke?