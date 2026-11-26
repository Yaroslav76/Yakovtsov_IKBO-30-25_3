#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"
asm examples/copy_array.yaml build/copy_array.bin
vm build/copy_array.bin build/copy_array.json --range 200:209
echo
echo "дамп build/copy_array.json:"
cat build/copy_array.json
"$PY" - <<'PYEOF'
import json
cells = json.load(open("build/copy_array.json"))["memory"]
first = [cells[str(a)] for a in range(200, 205)]
second = [cells[str(a)] for a in range(205, 210)]
print("исходный массив:", first)
print("копия:          ", second)
print("массивы равны:  ", first == second)
PYEOF
asm examples/errors/error_in_third.yaml build/error.bin
printf -- '- read\n' > build/underflow.yaml
asm build/underflow.yaml build/underflow.bin
vm build/underflow.bin build/dump.json --range 0:3
printf '\x01\x00\x00' > build/bad_opcode.bin
vm build/bad_opcode.bin build/dump.json --range 0:3
printf '\x07\x00' > build/bad_size.bin
vm build/bad_size.bin build/dump.json --range 0:3
vm no_such.bin build/dump.json --range 0:3
vm build/copy_array.bin build/dump.json --range 9:1
vm build/copy_array.bin build/dump.json --range 0:9000
vm build/copy_array.bin build/dump.json --range abc
vm build/copy_array.bin /no/such/dir/dump.json --range 0:3
