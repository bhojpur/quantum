# -*- coding: utf-8 -*-

# Copyright (c) 2018 Bhojpur Consulting Private Limited, India. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Tests for divya.backends._printer.py.
"""

import pytest

from divya import MainEngine
from divya.backends import _printer
from divya.cengines import DummyEngine, InstructionFilter, NotYetMeasuredError
from divya.meta import LogicalQubitIDTag
from divya.ops import NOT, Allocate, Command, H, Measure, T
from divya.types import WeakQubitRef

def test_command_printer_is_available():
    inline_cmd_printer = _printer.CommandPrinter()
    cmd_printer = _printer.CommandPrinter()

    def available_cmd(self, cmd):
        return cmd.gate == H

    filter = InstructionFilter(available_cmd)
    eng = MainEngine(backend=cmd_printer, engine_list=[inline_cmd_printer, filter])
    qubit = eng.allocate_qubit()
    cmd0 = Command(eng, H, (qubit,))
    cmd1 = Command(eng, T, (qubit,))
    assert inline_cmd_printer.is_available(cmd0)
    assert not inline_cmd_printer.is_available(cmd1)
    assert cmd_printer.is_available(cmd0)
    assert cmd_printer.is_available(cmd1)

def test_command_printer_accept_input(monkeypatch):
    cmd_printer = _printer.CommandPrinter()
    eng = MainEngine(backend=cmd_printer, engine_list=[DummyEngine()])
    monkeypatch.setattr(_printer, "input", lambda x: 1)
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 1
    monkeypatch.setattr(_printer, "input", lambda x: 0)
    qubit = eng.allocate_qubit()
    NOT | qubit
    Measure | qubit
    assert int(qubit) == 0

def test_command_printer_measure_no_control():
    qb1 = WeakQubitRef(engine=None, idx=1)
    qb2 = WeakQubitRef(engine=None, idx=2)

    printer = _printer.CommandPrinter()
    printer.is_last_engine = True
    with pytest.raises(ValueError):
        printer._print_cmd(Command(engine=None, gate=Measure, qubits=([qb1],), controls=[qb2]))

def test_command_printer_no_input_default_measure():
    cmd_printer = _printer.CommandPrinter(accept_input=False)
    eng = MainEngine(backend=cmd_printer, engine_list=[DummyEngine()])
    qubit = eng.allocate_qubit()
    NOT | qubit
    Measure | qubit
    assert int(qubit) == 0

def test_command_printer_measure_mapped_qubit():
    eng = MainEngine(_printer.CommandPrinter(accept_input=False), [])
    qb1 = WeakQubitRef(engine=eng, idx=1)
    qb2 = WeakQubitRef(engine=eng, idx=2)
    cmd0 = Command(engine=eng, gate=Allocate, qubits=([qb1],))
    cmd1 = Command(
        engine=eng,
        gate=Measure,
        qubits=([qb1],),
        controls=[],
        tags=[LogicalQubitIDTag(2)],
    )
    with pytest.raises(NotYetMeasuredError):
        int(qb1)
    with pytest.raises(NotYetMeasuredError):
        int(qb2)
    eng.send([cmd0, cmd1])
    eng.flush()
    with pytest.raises(NotYetMeasuredError):
        int(qb1)
    assert int(qb2) == 0