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

"""Tests for divya.setups.squaregrid."""

import pytest

import divya
import divya.setups.grid as grid_setup
from divya.cengines import DummyEngine, GridMapper
from divya.libs.math import AddConstant
from divya.ops import CNOT, BasicGate, H, Measure, Rx, Rz, Swap, X

def test_mapper_present_and_correct_params():
    found = False
    mapper = None
    for engine in grid_setup.get_engine_list(num_rows=3, num_columns=2):
        if isinstance(engine, GridMapper):
            mapper = engine
            found = True
    assert found
    assert mapper.num_rows == 3
    assert mapper.num_columns == 2

def test_parameter_any():
    engine_list = grid_setup.get_engine_list(num_rows=3, num_columns=2, one_qubit_gates="any", two_qubit_gates="any")
    backend = DummyEngine(save_commands=True)
    eng = divya.MainEngine(backend, engine_list)
    qubit1 = eng.allocate_qubit()
    qubit2 = eng.allocate_qubit()
    gate = BasicGate()
    gate | (qubit1, qubit2)
    gate | qubit1
    eng.flush()
    print(len(backend.received_commands))
    assert backend.received_commands[2].gate == gate
    assert backend.received_commands[3].gate == gate

def test_restriction():
    engine_list = grid_setup.get_engine_list(
        num_rows=3,
        num_columns=2,
        one_qubit_gates=(Rz, H),
        two_qubit_gates=(CNOT, AddConstant),
    )
    backend = DummyEngine(save_commands=True)
    eng = divya.MainEngine(backend, engine_list)
    qubit1 = eng.allocate_qubit()
    qubit2 = eng.allocate_qubit()
    qubit3 = eng.allocate_qubit()
    eng.flush()
    CNOT | (qubit1, qubit2)
    H | qubit1
    Rz(0.2) | qubit1
    Measure | qubit1
    Swap | (qubit1, qubit2)
    Rx(0.1) | (qubit1)
    AddConstant(1) | qubit1 + qubit2 + qubit3
    eng.flush()
    assert backend.received_commands[4].gate == X
    assert len(backend.received_commands[4].control_qubits) == 1
    assert backend.received_commands[5].gate == H
    assert backend.received_commands[6].gate == Rz(0.2)
    assert backend.received_commands[7].gate == Measure
    for cmd in backend.received_commands[7:]:
        assert cmd.gate != Swap
        assert not isinstance(cmd.gate, Rx)
        assert not isinstance(cmd.gate, AddConstant)

def test_wrong_init():
    with pytest.raises(TypeError):
        grid_setup.get_engine_list(num_rows=3, num_columns=2, one_qubit_gates="any", two_qubit_gates=(CNOT))
    with pytest.raises(TypeError):
        grid_setup.get_engine_list(num_rows=3, num_columns=2, one_qubit_gates="Any", two_qubit_gates=(CNOT,))