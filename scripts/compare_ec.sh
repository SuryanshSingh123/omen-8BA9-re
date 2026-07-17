#!/usr/bin/env bash

set -e

if [[ $# -ne 2 ]]; then
    echo "Usage:"
    echo "  $0 before.txt after.txt"
    exit 1
fi

echo "========================================"
echo "EC Dump Comparison"
echo "========================================"
echo

diff -y --suppress-common-lines "$1" "$2" || true