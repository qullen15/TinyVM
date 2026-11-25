"""Юнит-тесты этапа 4: команда popcnt."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assembler import assemble, OPCODES
from vm import popcount, new_memory, execute, run_program

CASES = [(0, 0), (1, 1), (8, 1), (13, 3), (255, 8)]
INDIRECT = (300, 3)
PROGRAM = [
    {"a": 4, "b": 100, "c": 13},
    {"a": 4, "b": 101, "c": 255},
    {"a": 4, "b": 20, "c": 200},
    {"a": 4, "b": 21, "c": 201},
    {"a": 5, "b": 100, "c": 20},
    {"a": 5, "b": 101, "c": 21},
]
RESULTS = {200: 3, 201: 8}


class TestPopcount:
    """Подсчёт единиц в двоичной записи числа."""

    def test_values(self):
        for value, expected in CASES:
            assert popcount(value) == expected


class TestDoPopcnt:
    """Выполнение команды popcnt над памятью."""

    def test_indirect_result(self):
        memory = new_memory()
        memory[10] = 13
        memory[20] = 300
        error = execute({"a": OPCODES["popcnt"], "b": 10, "c": 20}, memory)
        assert error is None
        address, expected = INDIRECT
        assert memory[address] == expected

    def test_bad_source(self):
        memory = new_memory()
        memory[20] = 300
        instruction = {"a": OPCODES["popcnt"], "b": len(memory), "c": 20}
        assert execute(instruction, memory) is not None

    def test_bad_pointer(self):
        memory = new_memory()
        memory[10] = 13
        memory[20] = len(memory)
        instruction = {"a": OPCODES["popcnt"], "b": 10, "c": 20}
        assert execute(instruction, memory) is not None


class TestProgram:
    """Программа вычислений popcnt целиком."""

    def test_results_in_memory(self):
        memory = new_memory()
        assert run_program(assemble(PROGRAM), memory) is None
        for address, expected in RESULTS.items():
            assert memory[address] == expected