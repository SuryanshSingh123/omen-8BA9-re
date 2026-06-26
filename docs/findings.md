# Findings

## Hardware

- Model: OMEN 16-wd0xxx
- Board: 8BA9
- CPU: i7-13620H
- GPU: RTX 4060 Laptop

## Linux

- hp_wmi loads successfully.
- query 0x4c returns error 0x6.
- fan1_input always reports 0 RPM.
- fan2_input always reports 0 RPM.
- pwm1_enable exists.

## Windows

Pending investigation.

## Conclusion

Likely unsupported WMI implementation rather than broken hardware.