#!/usr/bin/env bash
ROOT=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH="$ROOT"
case "$1" in
    asm) shift; exec python3 -m src.assembler "$@" ;;
    vm) shift; exec python3 -m src.interpreter "$@" ;;
    *) echo "использование: ./run.sh asm|vm аргументы"; exit 2 ;;
esac
