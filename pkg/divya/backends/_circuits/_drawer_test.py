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
Tests for divya.backends.circuits._drawer.py.
"""

import pytest

import divya.backends._circuits._drawer as _drawer
from divya import MainEngine
from divya.backends._circuits._drawer import CircuitDrawer, CircuitItem
from divya.ops import CNOT, Command, H, Measure, X
from divya.types import WeakQubitRef

@pytest.mark.parametrize("ordered", [False, True])
def test_drawer_getlatex(ordered):
    old_latex = _drawer.to_latex
    _drawer.to_latex = lambda x, drawing_order, draw_gates_in_parallel: x

    drawer = CircuitDrawer()
    drawer.set_qubit_locations({0: 1, 1: 0})

    drawer2 = CircuitDrawer()

    eng = MainEngine(drawer, [drawer2])
    qureg = eng.allocate_qureg(2)
    H | qureg[1]
    H | qureg[0]
    X | qureg[0]
    CNOT | (qureg[0], qureg[1])

    lines = drawer2.get_latex(ordered=ordered)
    assert len(lines) == 2
    assert len(lines[0]) == 4
    assert len(lines[1]) == 3

    # check if it was sent on correctly:
    lines = drawer.get_latex(ordered=ordered)
    assert len(lines) == 2
    assert len(lines[0]) == 3
    assert len(lines[1]) == 4

    _drawer.to_latex = old_latex

def test_drawer_measurement():
    drawer = CircuitDrawer(default_measure=0)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 0

    drawer = CircuitDrawer(default_measure=1)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 1

    drawer = CircuitDrawer(accept_input=True)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()

    old_input = _drawer.input

    _drawer.input = lambda x: '1'
    Measure | qubit
    assert int(qubit) == 1
    _drawer.input = old_input

    qb1 = WeakQubitRef(engine=eng, idx=1)
    qb2 = WeakQubitRef(engine=eng, idx=2)
    with pytest.raises(ValueError):
        eng.backend._print_cmd(Command(engine=eng, gate=Measure, qubits=([qb1],), controls=[qb2]))

def test_drawer_qubitmapping():
    drawer = CircuitDrawer()
    # mapping should still work (no gate has been applied yet)
    valid_mappings = [{0: 1, 1: 0}, {2: 1, 1: 2}]
    for valid_mapping in valid_mappings:
        drawer.set_qubit_locations(valid_mapping)
        drawer = CircuitDrawer()

    # invalid mapping should raise an error:
    invalid_mappings = [{3: 1, 0: 2}, {0: 1, 2: 1}]
    for invalid_mapping in invalid_mappings:
        drawer = CircuitDrawer()
        with pytest.raises(RuntimeError):
            drawer.set_qubit_locations(invalid_mapping)

    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()  # noqa: F841
    # mapping has begun --> can't assign it anymore
    with pytest.raises(RuntimeError):
        drawer.set_qubit_locations({0: 1, 1: 0})

class MockEngine(object):
    def is_available(self, cmd):
        self.cmd = cmd
        self.called = True
        return False

def test_drawer_isavailable():
    drawer = CircuitDrawer()
    drawer.is_last_engine = True

    assert drawer.is_available(None)
    assert drawer.is_available("Everything")

    mock_engine = MockEngine()
    mock_engine.called = False
    drawer.is_last_engine = False
    drawer.next_engine = mock_engine

    assert not drawer.is_available(None)
    assert mock_engine.called
    assert mock_engine.cmd is None

def test_drawer_circuititem():
    circuit_item = CircuitItem(1, 2, 3)
    assert circuit_item.gate == 1
    assert circuit_item.lines == 2
    assert circuit_item.ctrl_lines == 3
    assert circuit_item.id == -1

    circuit_item2 = CircuitItem(1, 2, 2)
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.ctrl_lines = 3
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item

    circuit_item2.gate = 2
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.gate = 1
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item

    circuit_item2.lines = 1
    assert not circuit_item2 == circuit_item
    assert circuit_item2 != circuit_item

    circuit_item2.lines = 2
    assert circuit_item2 == circuit_item
    assert not circuit_item2 != circuit_item