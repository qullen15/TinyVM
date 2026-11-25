"""Юнит-тесты этапа 3: декодирование, память, исполнение, дамп."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assembler import encode_instruction, assemble, OPCODES
from vm import (decode_instruction, new_memory, read_cell, write_cell,
                execute, run_program, check_bounds, dump_xml, MEMORY_SIZE)
from interpreter import main

UNKNOWN_OPCODE = 1

INSTRUCTIONS = [
    {"a": 4, "b": 312, "c": 685},
    {"a": 0, "b": 778, "c": 797},
    {"a": 7, "b": 249, "c": 499},
    {"a": 5, "b": 333, "c": 3},
]
COPY_PROGRAM = [
    {"a": 4, "b": 100, "c": 11},
    {"a": 4, "b": 101, "c": 22},
    {"a": 4, "b": 10, "c": 100},
    {"a": 4, "b": 11, "c": 101},
    {"a": 4, "b": 20, "c": 200},
    {"a": 4, "b": 21, "c": 201},
    {"a": 0, "b": 10, "c": 300},
    {"a": 7, "b": 300, "c": 20},
    {"a": 0, "b": 11, "c": 300},
    {"a": 7, "b": 300, "c": 21},
]


class TestDecode:
    """Декодирование байтов обратно в поля."""

    def test_round_trip(self):
        for instruction in INSTRUCTIONS:
            data = encode_instruction(instruction)
            result, error = decode_instruction(data)
            assert error is None
            assert result == instruction

    def test_wrong_size(self):
        result, error = decode_instruction(b"\x00")
        assert result is None
        assert "байт" in error

    def test_unknown_opcode(self):
        data = encode_instruction({"a": 1, "b": 0, "c": 0})
        result, error = decode_instruction(data)
        assert result is None
        assert "неизвестный код" in error


class TestMemory:
    """Чтение и запись ячеек памяти."""

    def test_write_read(self):
        memory = new_memory()
        assert write_cell(memory, 5, 42) is None
        value, error = read_cell(memory, 5)
        assert error is None
        assert value == 42

    def test_out_of_bounds(self):
        memory = new_memory()
        assert write_cell(memory, MEMORY_SIZE, 1) is not None
        value, error = read_cell(memory, -1)
        assert value is None
        assert error is not None


class TestExecute:
    """Выполнение команд над памятью."""

    def test_const(self):
        memory = new_memory()
        error = execute({"a": OPCODES["const"], "b": 10, "c": 77}, memory)
        assert error is None
        assert memory[10] == 77

    def test_load_indirect(self):
        memory = new_memory()
        memory[10] = 100
        memory[100] = 55
        error = execute({"a": OPCODES["load"], "b": 10, "c": 20}, memory)
        assert error is None
        assert memory[20] == 55

    def test_store_indirect(self):
        memory = new_memory()
        memory[30] = 88
        memory[40] = 200
        error = execute({"a": OPCODES["store"], "b": 30, "c": 40}, memory)
        assert error is None
        assert memory[200] == 88

    def test_unknown_handler(self):
        memory = new_memory()
        instruction = {"a": UNKNOWN_OPCODE, "b": 0, "c": 0}
        assert execute(instruction, memory) is not None

class TestRunProgram:
    """Цикл интерпретации целиком."""

    def test_copy_array(self):
        memory = new_memory()
        assert run_program(assemble(COPY_PROGRAM), memory) is None
        assert memory[200] == 11
        assert memory[201] == 22
        assert memory[100] == 11

    def test_empty_code(self):
        assert run_program(b"", new_memory()) is None


class TestBounds:
    """Проверка диапазона адресов дампа."""

    def test_valid(self):
        assert check_bounds(0, 10, MEMORY_SIZE) is None

    def test_negative_start(self):
        assert check_bounds(-1, 10, MEMORY_SIZE) is not None

    def test_reversed(self):
        assert check_bounds(10, 5, MEMORY_SIZE) is not None

    def test_too_big(self):
        assert check_bounds(0, MEMORY_SIZE, MEMORY_SIZE) is not None


class TestDumpXml:
    """Формирование XML-дампа."""

    def test_contains_cells(self):
        memory = new_memory()
        memory[200] = 11
        text = dump_xml(memory, 200, 201)
        assert '<cell address="200">11</cell>' in text
        assert '<cell address="201">0</cell>' in text


class TestInterpreterMain:
    """Точка входа интерпретатора."""

    def test_writes_dump(self, tmp_path, capsys, monkeypatch):
        binary = tmp_path / "copy.bin"
        binary.write_bytes(assemble(COPY_PROGRAM))
        dump = tmp_path / "out" / "copy.xml"
        monkeypatch.setattr(sys, "argv", [
            "interpreter.py", "--binary", str(binary),
            "--dump", str(dump), "--start", "200", "--end", "201"])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert "11" in dump.read_text(encoding="utf-8")
        assert "Дамп" in out

    def test_missing_binary(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "interpreter.py", "--binary", str(tmp_path / "no.bin"),
            "--dump", str(tmp_path / "d.xml"), "--start", "0", "--end", "1"])
        with pytest.raises(SystemExit) as exc:
            main()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "не удалось прочитать" in err

    def test_bad_range(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "interpreter.py", "--binary", str(tmp_path / "x.bin"),
            "--dump", str(tmp_path / "d.xml"),
            "--start", "10", "--end", "5"])
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1