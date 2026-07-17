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