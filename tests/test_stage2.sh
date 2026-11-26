#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"
asm examples/spec_tests.yaml build/spec_tests.bin --test
"$PY" -m src.assembler examples/spec_tests.yaml build/spec_tests.bin \
    --test | grep '^0x' > build/spec_bytes.txt
check tests/expected/spec_bytes.txt build/spec_bytes.txt
printf '\xBF\x1E\x00\x07\x00\x00\x83\x3A\x01\xAC\xE7\x01' \
    > build/spec_expected.bin
if cmp -s build/spec_tests.bin build/spec_expected.bin; then
    echo "СОВПАДАЕТ двоичный файл с эталонными 12 байтами"
fi
echo "содержимое build/spec_tests.bin:"
od -An -tx1 -v build/spec_tests.bin
asm examples/spec_tests.yaml /no/such/dir/out.bin
asm examples/errors/error_in_third.yaml build/error.bin
