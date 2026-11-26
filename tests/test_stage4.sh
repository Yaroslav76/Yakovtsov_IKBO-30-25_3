#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"
asm examples/sub_demo.yaml build/sub_demo.bin
vm build/sub_demo.bin build/sub_demo.json --range 300:305
echo
echo "дамп build/sub_demo.json:"
cat build/sub_demo.json
"$PY" - <<'PYEOF'
import json
cells = json.load(open("build/sub_demo.json"))["memory"]
value = {int(a): v for a, v in cells.items()}
rules = [(302, 300, 301), (303, 301, 300), (304, 300, 300), (305, 302, 303)]
for target, first, second in rules:
    expected = value[first] - value[second]
    verdict = "верно" if value[target] == expected else "НЕВЕРНО"
    print(f"[{target}] = [{first}] - [{second}] = {value[first]} - "
          f"{value[second]} = {expected}; в памяти {value[target]}: {verdict}")
PYEOF
printf -- '- load_const: 100\n- write: 300\n- load_const: 58\n- write: 301\n- load_const: 300\n- sub: 301\n- read\n' > build/neg_address.yaml
asm build/neg_address.yaml build/neg_address.bin
vm build/neg_address.bin build/dump.json --range 0:3
printf -- '- sub: 300\n' > build/sub_empty.yaml
asm build/sub_empty.yaml build/sub_empty.bin
vm build/sub_empty.bin build/dump.json --range 0:3
