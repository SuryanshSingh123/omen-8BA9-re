# Hypothesis 1

EC register 0x95 returns a thermal profile value unsupported by hp-wmi

## Evidence:
platform_profile_omen_get_ec() only accepts a fixed set of thermal profile values
Any unknown value results in -EINVAL (-22)

## Status:
Probably true

# Hypothesis 2

The EC read itself fails

## Evidence:
ec_read() may return an error before any value is decoded

## Status:
Unconfirmed
Need to inspect ec_read() implementation or print the returned value