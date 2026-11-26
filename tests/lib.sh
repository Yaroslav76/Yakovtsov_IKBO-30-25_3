cd "$(dirname "$0")/.." || exit 1
export PYTHONPATH=.
PY=${PYTHON:-python3}
mkdir -p build
asm() {
    echo
    echo "\$ python3 -m src.assembler $*"
    "$PY" -u -m src.assembler "$@" 2>&1
    echo "[код возврата: $?]"
}
vm() {
    echo
    echo "\$ python3 -m src.interpreter $*"
    "$PY" -u -m src.interpreter "$@" 2>&1
    echo "[код возврата: $?]"
}
check() {
    if diff -u "$1" "$2" > /dev/null; then
        echo "СОВПАДАЕТ с ожидаемым: $1"
    else
        echo "РАСХОЖДЕНИЕ с $1"
        diff -u "$1" "$2"
    fi
}
