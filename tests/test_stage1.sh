#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"
asm examples/spec_tests.yaml build/spec_tests.bin --test
"$PY" -m src.assembler examples/spec_tests.yaml build/spec_tests.bin \
    --test | grep '^A=' > build/spec_fields.txt
check tests/expected/spec_fields.txt build/spec_fields.txt
for f in examples/errors/*.yaml; do
    asm "$f" build/error.bin
done
asm no_such.yaml build/error.bin
asm examples build/error.bin
