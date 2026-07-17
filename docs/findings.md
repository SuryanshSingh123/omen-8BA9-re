# Findings

## Hardware

- Model: HP OMEN 16-wd0xxx
- Board: 8BA9
- CPU: Intel Core i7-13620H
- GPU: NVIDIA GeForce RTX 4060 Laptop

## Linux

- `hp_wmi` loads successfully.
- Previous kernel logs reported:
  - `query 0x4c returned error 0x6`
- Current kernel logs report:
  - `Failed to read current platform profile (-22)`
- `fan1_input` consistently reports `0 RPM`.
- `fan2_input` consistently reports `0 RPM`.
- `pwm1_enable` is present.
- Driver tracing shows platform profile reads occur through:
  - `platform_profile_omen_get_ec()`
  - `omen_thermal_profile_get()`
  - `ec_read()`
- Board `8BA9` is **NOT** present in the driver's known OMEN thermal profile board tables

## Windows

- Fans operate pretty normal through OMEN Gaming Hub
- OMEN Gaming Hub installs and uses:
  - `HPCustomCapDriver`
  - `HPOmenCustomCapDriver`
- ACPI device `HPIC004` is present and active

## Driver observations

- hp_wmi now loads correctly after kernel update
- The previous WMI query failure (0x4c → error 0x6) no longer occurs
- The driver now reaches platform_profile_omen_get_ec() instead
- platform_profile_omen_get_ec() reads EC offset 0x95 using ec_read()
- platform profile retrieval reaches ec_read() before returning -EINVAL

## Embedded Controller

- hp_wmi uses ACPI EC reads (`ec_read()`), not direct `/sys/kernel/debug/ec` access
- Kernel is compiled with `CONFIG_ACPI_EC_DEBUGFS=m`
- `ec_sys` module is unavailable on this kernel
- `/sys/kernel/debug/ec/` is therefore unavailable

## Current evidence

Working

- HP-specific WMI device detected
- DKMS driver loads
- EC read functions are executed
- Windows fan control works

Not working

- Platform profile initialization
- Fan RPM reporting
- Fan control

### Thermal profile values expected by hp-wmi

The driver reads EC register `0x95` and only accepts the following values:

V0:
- 0x00 = Balanced
- 0x01 = Performance
- 0x02 = Cool

V1:
- 0x30 = Balanced
- 0x31 = Performance
- 0x50 = Cool

Any other value causes the driver to return `-EINVAL`, producing

Failed to read current platform profile (-22)

## Boot behavior (Most interesting one up until now)

After rebooting directly from Windows to Linux:

- Both fans immediately spin at maximum speed.
- Maximum speed persists for approximately one minute.
- Fans then return to normal automatic control.

This behavior is reproducible after changing thermal modes in Windows.

I'd guess it to be a EC watchdog/timeout

## Embedded Controller

- EC register 0x95 does not contain a thermal profile.
- Register 0x95 consistently contains value 0x43 (translates to ASCII 67 im not kidding, which is character 'C').
- Surrounding registers decode to ASCII:

333-AC-12WK06083 (some build number?? manufacturing ID??)

- This strongly indicates that the EC memory layout differs from what hp-wmi expects on board 8BA9.

>Basically, driver asks the EC "Are you in Balanced (0x30), Performance (0x31), or Cool (0x50)?", to which the EC genuinely responds "67" or "C.", and the driver goes insane.
> Just kidding, EC's raw response is "0x43", which the driver doesn't know about, returning ```-EINVAL```.