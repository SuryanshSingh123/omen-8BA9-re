#!/usr/bin/env python3

import argparse
import sys
from collections import defaultdict

from dump_diff import parse_dump


def main():
    parser = argparse.ArgumentParser(
        description="Find EC addresses that are stable within a labeled state "
        "but differ across states (e.g. thermal profiles), filtering out "
        "noisy bytes like fan RPM or temperature counters."
    )
    parser.add_argument(
        "dumps",
        nargs="+",
        help="label=path pairs, e.g. balanced=dump1.txt performance=dump2.txt. "
        "Repeat a label with multiple dumps to filter out jitter.",
    )
    parser.add_argument("--csv", help="Write candidate addresses to CSV")
    args = parser.parse_args()

    by_label = defaultdict(list)
    for entry in args.dumps:
        if "=" not in entry:
            sys.exit(f"Invalid argument: {entry!r} (expected label=path)")
        label, path = entry.split("=", 1)
        by_label[label].append(parse_dump(path))

    if len(by_label) < 2:
        sys.exit("Need at least two distinct labels to correlate")

    addresses = set()
    for dumps in by_label.values():
        for dump in dumps:
            addresses.update(dump.keys())

    stable_value = {}
    noisy = set()
    for label, dumps in by_label.items():
        for addr in addresses:
            values = {dump.get(addr) for dump in dumps}
            if len(values) > 1:
                noisy.add(addr)
            else:
                stable_value[(label, addr)] = values.pop()

    candidates = []
    for addr in sorted(addresses):
        if addr in noisy:
            continue
        per_label = {
            label: stable_value.get((label, addr)) for label in by_label
        }
        if len(set(per_label.values())) > 1:
            candidates.append((addr, per_label))

    labels = sorted(by_label)
    print("=" * 48)
    print("HP OMEN EC Correlate")
    print("=" * 48)
    print(f"Labels: {', '.join(labels)}")
    print(f"Noisy addresses excluded: {len(noisy)}")
    print()

    for addr, per_label in candidates:
        row = " ".join(
            f"{label}=0x{per_label[label]:02X}"
            if per_label[label] is not None
            else f"{label}=--"
            for label in labels
        )
        print(f"0x{addr:02X} : {row}")

    print()
    print(f"Candidate addresses : {len(candidates)} / {len(addresses)}")

    if args.csv:
        import csv

        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Address", *labels])
            for addr, per_label in candidates:
                writer.writerow(
                    [f"0x{addr:02X}"]
                    + [
                        "--" if per_label[label] is None else f"0x{per_label[label]:02X}"
                        for label in labels
                    ]
                )
        print(f"CSV written to {args.csv}")


if __name__ == "__main__":
    main()
