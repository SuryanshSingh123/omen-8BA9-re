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
- Board `8BA9` **WAS NOT** present in the driver's known OMEN thermal profile board tables (it is now after kernel update, but there's another issue)

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

## Enlightenment (RWEverything)

This is definitely the biggest achievement in this repository till now.

Up until now I had been stuck in a loop of booting back and forth into linux and windows to get dumps. However, I found a tool that allows to see the EC registers live, and even write them, while being booted into windows. The tool was RWEverything. This was basicallt the holy grain of analyzing EC dumps, or more like live registers now. It helped me discover more than I had in the entire month, in the same boot.

Incredibly useful tool.

## Profile Register (IMPORTANT)

As mentioned in tests.md, I found out the profile register, and confirmed it. 

It has the expected bytes for its respective profiles as well (0x30, 0x31).

However, ECO and Balanced had the same byte somehow (0x30). My assumption is that ECO is probably a variation of balanced, and the register only divides profile in "perfomance or not perfomance". I am confident about this assumption, since ECO mode does feel like balanced mode but 60hz refresh rate and lower brightness, though there would be more changes on the backend of course.

## Looking back at hp-wmi.c...

This is really interesting, and no I do not wanna sound like Chat GPT but it really is.

```C
static const struct thermal_profile_params omen_v1_thermal_params = {
	.performance	= HP_OMEN_V1_THERMAL_PROFILE_PERFORMANCE,
	.balanced	= HP_OMEN_V1_THERMAL_PROFILE_DEFAULT,
	.low_power	= HP_OMEN_V1_THERMAL_PROFILE_DEFAULT,
	.ec_tp_offset	= HP_VICTUS_S_EC_THERMAL_PROFILE_OFFSET, /*They're using the Victus S offsets for new v1 boards.*/
};
```

And what is the offset for Victus S models?

```C
enum hp_ec_offsets {
	HP_EC_OFFSET_UNKNOWN				= 0x00,
	HP_NO_THERMAL_PROFILE_OFFSET			= 0x01,
	HP_VICTUS_S_EC_THERMAL_PROFILE_OFFSET		= 0x59,/*the SAME register i JUST found for my omen board..*/
	HP_OMEN_EC_THERMAL_PROFILE_FLAGS_OFFSET		= 0x62,
	HP_OMEN_EC_THERMAL_PROFILE_TIMER_OFFSET		= 0x63,
	HP_OMEN_EC_THERMAL_PROFILE_OFFSET		= 0x95,
};
```

So, am I stupid for doing all that when technically the parameters were defined to be at 0x59 somewhere in the code?

Not really, if it was that robust I wouldn't have had problems with my fans or profiles in the first place.

More things:

```C
/* DMI Board names of Victus 16-r and Victus 16-s laptops */
static const struct dmi_system_id victus_s_thermal_profile_boards[] __initconst = {
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8A44") },
		.driver_data = (void *)&omen_v1_legacy_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8A4D") },
		.driver_data = (void *)&omen_v1_legacy_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BAB") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BBE") },
		.driver_data = (void *)&victus_s_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BC2") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BCA") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BCD") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BD4") },
		.driver_data = (void *)&victus_s_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8BD5") },
		.driver_data = (void *)&victus_s_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8C76") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8C77") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8C78") },
		.driver_data = (void *)&omen_v1_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8C99") },
		.driver_data = (void *)&victus_s_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8C9C") },
		.driver_data = (void *)&victus_s_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8D41") },
		.driver_data = (void *)&omen_v1_no_ec_thermal_params,
	},
	{
		.matches = { DMI_MATCH(DMI_BOARD_NAME, "8D87") },
		.driver_data = (void *)&omen_v1_no_ec_thermal_params,
	},
	{},
};
```
Victus 16-r and Victus 16-s laptop boards, yeah sure. They literally have more omen boards here.

What's more is that although 8BA9 is in the thermal_profiles table and timed_thermal_profiles table now (as far as i remember), it is **NOT** here.

My research till now did prove that 8BA9 is highly likely to work with the same offsets as the rest of the v1 boards here (exclude legacy). It has the same register and the same byte mapping as mentioned in the driver.

**IMPORTANT**
- ```0x59``` is stuck at ```0x00``` throughout Linux.

## 0x59 changed?

I only said it was stuck at 0x00 looking at the dumps in this repo, I just realized that it had changed to 0x01 in my current dumps.

Weird, its probably related to from which state in windows I rebooted into linux, since the dumps in this repo were taken after a reboot from ECO Mode in Windows, and later I switched to Balance.

---

## END OF FINDINGS :)