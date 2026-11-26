@echo off
set PYTHONPATH=%~dp0
if "%1"=="asm" (
    shift
    python -m src.assembler %*
) else if "%1"=="vm" (
    shift
    python -m src.interpreter %*
) else (
    echo использование: run.bat asm^|vm аргументы
    exit /b 2
)
