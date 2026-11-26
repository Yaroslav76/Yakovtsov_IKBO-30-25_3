#!/usr/bin/env bash
. "$(dirname "$0")/lib.sh"
for n in 1 2 3; do
    asm examples/vector_sub_$n.yaml build/vector_sub_$n.bin
    vm build/vector_sub_$n.bin build/vector_sub_$n.json --range 400:419
    echo "дамп build/vector_sub_$n.json:"
    cat build/vector_sub_$n.json
    "$PY" - $n <<'PYEOF'
import json
import sys

sys.path.insert(0, "tests")
from make_examples import VECTORS

number = sys.argv[1]
kind, first, second = VECTORS[f"vector_sub_{number}"]
memory = json.load(open(f"build/vector_sub_{number}.json"))["memory"]
cells = [memory[str(a)] for a in range(400, 420)]
expected = [a - b for a, b in zip(first, second)]
print(f"случай: {kind}")
print("Вектор1 (400..409):         ", cells[:10])
print("Вектор2 до (410..419):      ", second)
print("Вектор2 после (410..419):   ", cells[10:])
print("ожидается Вектор1 - Вектор2:", expected)
print("Вектор1 не изменился:       ", cells[:10] == first)
print("результат верный:           ", cells[10:] == expected)
PYEOF
done
