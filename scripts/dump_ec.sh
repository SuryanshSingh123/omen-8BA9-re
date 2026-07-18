#!/usr/bin/env bash
set -e

OUT="${1:-ec_dump_$(date +%Y%m%d_%H%M%S).txt}"

sudo dmesg | grep -A260 "Full EC dump" > "$OUT"

echo "Saved dump to $OUT"