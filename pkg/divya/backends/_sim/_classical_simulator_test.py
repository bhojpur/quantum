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

import pytest

from divya import MainEngine
from divya.cengines import (
    AutoReplacer,
    BasicMapperEngine,
    DecompositionRuleSet,
    DummyEngine,
)
from divya.ops import NOT, All, BasicMathGate, C, Measure, X, Y
from divya.types import WeakQubitRef

from ._classical_simulator import ClassicalSimulator
from ._simulator_test import mapper  # noqa: F401

def test_simulator_read_write(mapper):  # noqa: F811
    engine_list = []
    if mapper is not None:
        engine_list.append(mapper)
    sim = ClassicalSimulator()
    eng = MainEngine(sim, engine_list)
    a = eng.allocate_qureg(32)
    b = eng.allocate_qureg(32)

    assert sim.read_register(a) == 0
    assert sim.read_register(b) == 0
    assert sim.read_bit(a[0]) == 0
    assert sim.read_bit(b[0]) == 0

    sim.write_register(a, 123)
    sim.write_register(b, 456)
    assert sim.read_register(a) == 123
    assert sim.read_register(b) == 456
    assert sim.read_bit(a[0]) == 1
    assert sim.read_bit(b[0]) == 0

    sim.write_bit(b[0], 1)
    assert sim.read_register(a) == 123
    assert sim.read_register(b) == 457
    assert sim.read_bit(a[0]) == 1
    assert sim.read_bit(b[0]) == 1

def test_simulator_triangle_increment_cycle(mapper):  # noqa: F811
    engine_list = []
    if mapper is not None:
        engine_list.append(mapper)
    sim = ClassicalSimulator()
    eng = MainEngine(sim, engine_list)

    a = eng.allocate_qureg(6)
    for t in range(1 << 6):
        assert sim.read_register(a) == t
        for i in range(6)[::-1]:
            C(X, i) | (a[:i], a[i])
    assert sim.read_register(a) == 0

def test_simulator_bit_repositioning(mapper):  # noqa: F811
    engine_list = []
    if mapper is not None:
        engine_list.append(mapper)
    sim = ClassicalSimulator()
    eng = MainEngine(sim, engine_list)
    a = eng.allocate_qureg(4)
    b = eng.allocate_qureg(5)
    c = eng.allocate_qureg(6)
    sim.write_register(a, 9)
    sim.write_register(b, 17)
    sim.write_register(c, 33)
    for q in b:
        eng.deallocate_qubit(q)
        # Make sure that the qubit are marked as deleted
        assert q.id == -1
    assert sim.read_register(a) == 9
    assert sim.read_register(c) == 33

def test_simulator_arithmetic(mapper):  # noqa: F811
    class Offset(BasicMathGate):
        def __init__(self, amount):
            super().__init__(lambda x: (x + amount,))

    class Sub(BasicMathGate):
        def __init__(self):
            super().__init__(lambda x, y: (x, y - x))

    engine_list = []
    if mapper is not None:
        engine_list.append(mapper)
    sim = ClassicalSimulator()
    eng = MainEngine(sim, engine_list)
    a = eng.allocate_qureg(4)
    b = eng.allocate_qureg(5)
    sim.write_register(a, 9)
    sim.write_register(b, 17)

    Offset(2) | a
    assert sim.read_register(a) == 11
    assert sim.read_register(b) == 17

    Offset(3) | b
    assert sim.read_register(a) == 11
    assert sim.read_register(b) == 20

    Offset(32 + 5) | b
    assert sim.read_register(a) == 11
    assert sim.read_register(b) == 25

    Sub() | (a, b)
    assert sim.read_register(a) == 11
    assert sim.read_register(b) == 14

    Sub() | (a, b)
    Sub() | (a, b)
    assert sim.read_register(a) == 11
    assert sim.read_register(b) == 24

    # also test via measurement:
    All(Measure) | a + b
    eng.flush()

    for i in range(len(a)):
        assert int(a[i]) == ((11 >> i) & 1)
    for i in range(len(b)):
        assert int(b[i]) == ((24 >> i) & 1)

def test_write_register_value_error_exception(mapper):  # noqa: F811
    engine_list = []
    if mapper is not None:
        engine_list.append(mapper)
    sim = ClassicalSimulator()
    eng = MainEngine(sim, engine_list)
    a = eng.allocate_qureg(3)
    with pytest.raises(ValueError):
        sim.write_register(a, -2)
    sim.write_register(a, 7)
    with pytest.raises(ValueError):
        sim.write_register(a, 8)

def test_x_gate_invalid():
    sim = ClassicalSimulator()
    eng = MainEngine(sim, [AutoReplacer(DecompositionRuleSet())])
    a = eng.allocate_qureg(2)

    with pytest.raises(ValueError):
        X | a

def test_available_gates():
    sim = ClassicalSimulator()
    eng = MainEngine(sim, [AutoReplacer(DecompositionRuleSet())])
    a = eng.allocate_qubit()
    X | a
    NOT | a
    Measure | a
    eng.flush()

def test_gates_are_forwarded_to_next_engine():
    sim = ClassicalSimulator()
    saving_eng = DummyEngine(save_commands=True)
    eng = MainEngine(saving_eng, [sim])
    a = eng.allocate_qubit()
    X | a
    a[0].__del__()
    assert len(saving_eng.received_commands) == 3

def test_wrong_gate():
    sim = ClassicalSimulator()
    eng = MainEngine(sim, [])
    a = eng.allocate_qubit()
    with pytest.raises(ValueError):
        Y | a

def test_runtime_error():
    sim = ClassicalSimulator()
    mapper = BasicMapperEngine()  # noqa: F811
    mapper.current_mapping = {}
    eng = MainEngine(sim, [mapper])
    with pytest.raises(RuntimeError):
        eng.backend.read_bit(WeakQubitRef(None, 1))