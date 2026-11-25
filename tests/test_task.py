"""Юнит-тесты этапа 5: тестовая задача и примеры программ."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from assembler import parse_program, assemble
from vm import new_memory, run_program

VECTOR_START = 100
RESULT_START = 200
TASK_RESULTS = [3, 8, 1, 0, 10]
POWERS_RESULTS = [1, 1, 1, 1, 1]
ONES_RESULTS = [2, 3, 4, 5, 6]
NEW_RESULTS = [2, 2, 3]
SOURCE_VALUES = [5, 6, 7]


def run_file(name):
    """Ассемблирует и исполняет программу из папки programs."""
    text = (ROOT / "programs" / name).read_text(encoding="utf-8")
    program, error = parse_program(text)
    assert error is None
    memory = new_memory()
    assert run_program(assemble(program), memory) is None
    return memory


class TestTask:
    """Тестовая задача: popcnt над вектором длины 5 на месте."""

    def test_in_place(self):
        memory = run_file("task.csv")
        for index, expected in enumerate(TASK_RESULTS):
            assert memory[VECTOR_START + index] == expected


class TestExamples:
    """Примеры программ с различными данными."""

    def test_powers_of_two(self):
        memory = run_file("example1.csv")
        for index, expected in enumerate(POWERS_RESULTS):
            assert memory[VECTOR_START + index] == expected

    def test_all_ones(self):
        memory = run_file("example2.csv")
        for index, expected in enumerate(ONES_RESULTS):
            assert memory[VECTOR_START + index] == expected

    def test_new_vector(self):
        memory = run_file("example3.csv")
        for index, expected in enumerate(NEW_RESULTS):
            assert memory[RESULT_START + index] == expected

    def test_source_unchanged(self):
        memory = run_file("example3.csv")
        for index, expected in enumerate(SOURCE_VALUES):
            assert memory[VECTOR_START + index] == expected