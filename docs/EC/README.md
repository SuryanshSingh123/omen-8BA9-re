# Again, Before you inspect:


## What even is an "Embedded Controller"
I can't explain everything about how an EC works, but that is needed to understand what's happening in this folder.


Just think of it like this: 

```text
                +----------------------+
                |       CPU/Linux      |
                +----------+-----------+
                           |
                    ACPI / EC I/O
                           |
                           v
        +--------------------------------------+
        |      Embedded Controller (EC MCU)    |
        |                                      |
        |  Firmware                            |
        |  +-------------------------------+   |
        |  | EC RAM / Register Space       |   |
        |  | Addresses        Bytes        |   |
        |  | 0x00              0x00        |   |
        |  | 0x01              0xFF        |   |
        |  | ....              ....        |   |
        |  | 0xFF              0xAB        |   |
        |  +-------------------------------+   |
        +------------------+-------------------+
                           |
      +--------------------+--------------------+
      |         |          |          |          |
     Fans     Temp      Battery   Power      Keyboard
    PWM/RPM   Sensors    Charging  Limits      LEDs
```
(ai made most of this diagram by the way(except the Addresses and Bytes list), i can not do that in markdown)

But I'll do the brief explanation,

## EC Registers
The EC is actually a tiny little computer for your computer, which even has its RAM, and a firmware it is running.
It is kind of like the low-level manager of system components.
The EC RAM (or EC register space) contains EC Registers, which are labels/addresses to store information in bytes (8 bits duh).
For better readablity, and because of conventions of the machine code, we read EC Registers and Byte values in HEX.
The registers are translated to decimal values, and the bytes (in hex) stored in them are translated to 8 bits.
For example, in the diagram, the register list starts from 0x00 and ends at 0xFF, that really is just 0 (0x00) and 255 (0xFF).
Therefore, this EC RAM has 256 registers (0-255).

## EC Bytes
Now, to the actually useful part, EC bytes are the values stored in registers. Every register exists under a predefined memory, which is under proprietary firmware, and we do NOT directly know which address is the label for what and how it even works, For example, 0xA4 could just be storing CPU temps, or battery, or anything. We don't know how the values inside work either, specifically for this case, we do not know what address stores the thermal profile or perhaps the fan RPM setting, neither do we know what value of the byte in it results in what. Notorious 0x43 could be balanced, perfomance, eco, or not a profile byte at all. 0x23 (just a random byte) could mean max fans, auto (bios control), manual setting, or neither and that it works completely different. 

## How hp_wmi works
What does hp_wmi do? It talks in high level language (C) to the ACPI/WMI layer, towards the BIOS, which then talks to the EC to, lets say, set your fans to max. BIOS is like an interpreter here, or a middle man/translator: it works with the what the functions in the driver want it to do, it acknowledges and then talks to the EC in low level language to fetch those addresses that we don't know about, and fetch or modify those bytes from the EC. The BIOS KNOWS what those bytes mean, so does the EC in its firmware and memory map. The driver doesn't know anything though, it only recieves either high end feedback from the BIOS, or byte values mostly without addresses (like in my debug function we got thermal_profile=0x43). In a single sentence, driver talks to BIOS, BIOS inquires/modifies EC, BIOS tells driver the job is done error-free (ret = 0) and what they wanted to know (data/thermal_profile = 0x43)

## Reverse Engineering: Knowing what you aren't supposed to, but need to know
The REAL problem arrives when I got hit with the fact that this may not be as linear as I thought. Sure, if "thermal_profile" was stored in a single address I could probably narrow it down through the dumps by getting to the some or luckily one address in the dump which had a "0x30" stored as a byte by just using CTRL+F in VSCodium. However, thing is that this "thermal_profile" may not be directly stored in an address at all. It could be written in firmware code, when some other addresses have a specific byte (like charging state is 0xFF/on, battery is 0xFF/full), then maybe "thermal_profile" is set to that byte value. That could be one way of implementing EC firmware, and I'm sure big corporations with crazy firmware engineers may have done so.

It could also be possible that this EC doesn't even use 0x30 for balanced, we don't realy know about it's memory map.

 "Can't you just google it or find it somewhere?". Well, yes. And no. HP BIOS update has the EC Firmware code bundled with it, yes it is. Problem is that even when I get to the main BIOS image of the EC code with its pretty signatures, when I will open the .bin file I will see nightmares. The nightmare is seeing stuff like:

```bin
 5A 20 9F 38 71 43 8A 
 ```
and so on... for who knows how many lines
Even upgrading this machine code a.k.a. hex to assembly, it doesn't really help because it'll be:

```asm
MOV R2, #0x43
CALL 0x7A
JMP 0x182
```
I haven't learnt assembly yet, and it turns out that even if I do, it is STILL some code with random bytes and zero comments inside to guide me about what byte means what.
Besides, what I'm currently trying to do can be done without even breaching the middle layer of the BIOS and EC Firmware code.

This, is reverse engineering. Going through an insane amount of trial and error, expecting things to change, to notice something new or prove something.
The specific layer that I am going through right now is termed as "Black Box Reverse Engineering", where you only make conclusions based on input and output, and not know anything about the firmware between, making it a "Black Box". I am only drawing conclusions from what I change myself on the system (input) and what the EC returns (output).

## About the dumps

The text files here contain dumps from a single boot -- not that valuable of course but it does help to cancel out the noisy bytes. The first dump is captured in the max fans state after rebooting from windows, and the rest are just subsequent dumps hoping to find a noticeable change for when the fans calm down from the aggressive state. Nothing much useful here yet, but I did learn to read dumps.

>NOTE: obsolete now, it's only a learning memory at this point but RWEverything changed it all.