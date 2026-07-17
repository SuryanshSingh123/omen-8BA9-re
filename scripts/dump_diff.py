#!/usr/bin/env python3


# Very very cool log for changes in EC bytes from dumps
import argparse
import csv
import re
import sys

EC_RE = re.compile(r"0x([0-9A-Fa-f]{2})\s*:\s*0x([0-9A-Fa-f]{2})")


def parse_dump(path):
    """
    Parse a hp_wmi EC dump from a dmesg/log file.
    Returns {address: value}
    """
    dump = {}

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = EC_RE.search(line)
            if m:
                addr = int(m.group(1), 16)
                value = int(m.group(2), 16)
                dump[addr] = value

    if len(dump) != 256:
        print(
            f"Warning: parsed {len(dump)} bytes from {path} (expected 256).",
            file=sys.stderr,
        )

    return dump


def main():
    parser = argparse.ArgumentParser(
        description="Compare two HP OMEN Embedded Controller dumps."
    )
    parser.add_argument("before", help="First dump")
    parser.add_argument("after", help="Second dump")
    parser.add_argument("--csv", help="Write changes to CSV")

    args = parser.parse_args()

    before = parse_dump(args.before)
    after = parse_dump(args.after)

    changed = []

    addresses = sorted(set(before.keys()) | set(after.keys()))

    print("=" * 48)
    print("HP OMEN EC Diff")
    print("=" * 48)

    for addr in addresses:
        b = before.get(addr)
        a = after.get(addr)

        if b != a:
            changed.append((addr, b, a))
            print(
                f"0x{addr:02X} : "
                f"{'--' if b is None else f'{b:02X}'}"
                f" -> "
                f"{'--' if a is None else f'{a:02X}'}"
            )

    print()
    print(f"Changed bytes : {len(changed)} / {len(addresses)}")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Address", "Before", "After"])

            for addr, b, a in changed:
                writer.writerow([
                    f"0x{addr:02X}",
                    "--" if b is None else f"0x{b:02X}",
                    "--" if a is None else f"0x{a:02X}",
                ])

        print(f"CSV written to {args.csv}")


if __name__ == "__main__":
    main()