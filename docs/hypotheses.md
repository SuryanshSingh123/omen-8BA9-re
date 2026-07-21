# Hypothesis 1

EC register 0x95 returns a thermal profile value unsupported by hp-wmi (found to be 0x43)

## Evidence:
platform_profile_omen_get_ec() only accepts a fixed set of thermal profile values
Any unknown value results in -EINVAL (-22)

## Status:
True

# Hypothesis 2

The EC read itself fails

## Evidence:
NOT USEFUL ANYMORE

## Status:
False (confirmed)

ec_read() works perfectly fine(returns ret = 0 which is a green flag).

# Hypothesis 3

Register 0x95 isn't even the thermal profile register in reality. (hp-wmi only assumes it to be across multiple HP Omen boards)

## Evidence:
It ALWAYS returns 0x43, no matter what profile I set in Windows and instantly capture a dump after rebooting into linux.
Seems more like a static register than a profile one that can vary.

## Status:
True (Actual Profile Register found to be different!)