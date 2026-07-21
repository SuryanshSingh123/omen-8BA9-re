# Internet findings!

## Alexis's patch

Somehow, searching for the string I got from the bytes near register 0x95 (333-AC-12WK06083) led me to a kernel.org bugzilla post, and even more luckily, it was pretty similar to my case, as it discussed about a broken fan curve table on 8BAD (pretty close to 8BA9). I got to know that weirdly enough, my motherbaord had been added in commit back in 2024, yet up until the recent kernel update, I am pretty sure it was nowhere to be found in hp-wmi.c.

This specific post just made me explore hp-wmi.c properly.

And the things I found there make this entire thing even more bizzare.

(Updated in findings after this commit)