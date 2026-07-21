# Research Log

## 2026-06-25

- Installed `hp-wmi-dkms`
- Fan RPM readings remained at `0 RPM`
- Verified that fan control was unavailable through the driver

## 2026-06-26

- Compared Embedded Controller (EC) dumps
- Identified several bytes that change with system state
- Installed OpenOMEN
- Fan control commands produced no observable effect

## 2026-06-29

- Booted into Windows for reverse engineering
- Identified drivers used by OMEN Gaming Hub:
  - `HPCustomCapDriver`
  - `HPOmenCustomCapDriver`
- Confirmed communication through the `HPIC004` ACPI device

## 2026-07-17

- Updated kernel from 7.1.3-arch1-3 → 7.1.3-arch2-1
- `hp_wmi` error changed, indicating a different execution path

### Command

```bash
sudo dmesg | grep -i hp_wmi
```

### Output (before)

```text
hp_wmi: query 0x4c returned error 0x6
```

### Output (after)

```text
[   44.422465] hp_wmi: Failed to read current platform profile (-22)
```

### Investigation

Tracing the driver revealed:

```text
platform_profile_omen_get_ec()
    └── omen_thermal_profile_get()
            └── ec_read(HP_OMEN_EC_THERMAL_PROFILE_OFFSET)
```

Unlike previous assumptions, this path reads directly from the Embedded Controller rather than issuing a WMI query

## 2026-07-21

- Booted into Windows.
- Installed RWEverything.
- Had to reboot twice to disable security settings that didn't allow vulnerable drivers to run (RW.sys)
- Opened the EC tab.
- Saw all 256 registers, refreshing every 1.5s, live.
- Set the offset to 500ms.
- Opened OMEN Gaming Hub and switched from balanced to perfomance multiple times. 

After finding the register and the analysis on hp-wmi.c again,

- Tried adding 8BA9 to ```victus_s_thermal_profile_boards```, in proper syntax:

```C
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BAB") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
```

- Rebuilt and installed dkms module (for the changes in code duh)
- And it did not work. The linux dumps still return thermal_profile = 0x43..
