"""Пакет УВМ: добавляет каталог src в путь импорта модулей."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
