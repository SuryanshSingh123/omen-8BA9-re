#!/usr/bin/env bash

set -e

EC="/sys/kernel/debug/ec/ec0/io"

if [[ ! -f "$EC" ]]; then
    echo "EC debug interface not found:"
    echo "  $EC"
    exit 1
fi

OUT="${1:-ec_dump_$(date +%Y%m%d_%H%M%S).txt}"

echo "# EC Dump" > "$OUT"
echo "# Date: $(date)" >> "$OUT"
echo "# Registers: 0x00-0xFF" >> "$OUT"
echo >> "$OUT"

sudo dd if="$EC" bs=256 count=1 status=none | xxd >> "$OUT"

echo "Saved dump to $OUT"