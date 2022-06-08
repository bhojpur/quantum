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

"""Tests for divya.cengines._testengine.py."""

from divya import MainEngine
from divya.cengines import DummyEngine, _testengine
from divya.ops import CNOT, Allocate, FlushGate, H, Rx

def test_compare_engine_str():
    compare_engine = _testengine.CompareEngine()
    eng = MainEngine(backend=compare_engine, engine_list=[DummyEngine()])
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    H | qb0
    CNOT | (qb0, qb1)
    eng.flush()
    expected = (
        "Qubit 0 : Allocate | Qureg[0], H | Qureg[0], "
        + "CX | ( Qureg[0], Qureg[1] )\nQubit 1 : Allocate | Qureg[1],"
        + " CX | ( Qureg[0], Qureg[1] )\n"
    )
    assert str(compare_engine) == expected


def test_compare_engine_is_available():
    compare_engine = _testengine.CompareEngine()
    assert compare_engine.is_available("Anything")

def test_compare_engine_receive():
    # Test that CompareEngine would forward commands
    backend = DummyEngine(save_commands=True)
    compare_engine = _testengine.CompareEngine()
    eng = MainEngine(backend=backend, engine_list=[compare_engine])
    qubit = eng.allocate_qubit()
    H | qubit
    eng.flush()
    assert len(backend.received_commands) == 3

def test_compare_engine():
    compare_engine0 = _testengine.CompareEngine()
    compare_engine1 = _testengine.CompareEngine()
    compare_engine2 = _testengine.CompareEngine()
    compare_engine3 = _testengine.CompareEngine()
    eng0 = MainEngine(backend=compare_engine0, engine_list=[DummyEngine()])
    eng1 = MainEngine(backend=compare_engine1, engine_list=[DummyEngine()])
    eng2 = MainEngine(backend=compare_engine2, engine_list=[DummyEngine()])
    eng3 = MainEngine(backend=compare_engine3, engine_list=[DummyEngine()])
    # reference circuit
    qb00 = eng0.allocate_qubit()
    qb01 = eng0.allocate_qubit()
    qb02 = eng0.allocate_qubit()
    H | qb00
    CNOT | (qb00, qb01)
    CNOT | (qb01, qb00)
    H | qb00
    Rx(0.5) | qb01
    CNOT | (qb00, qb01)
    Rx(0.6) | qb02
    eng0.flush()
    # identical circuit:
    qb10 = eng1.allocate_qubit()
    qb11 = eng1.allocate_qubit()
    qb12 = eng1.allocate_qubit()
    H | qb10
    Rx(0.6) | qb12
    CNOT | (qb10, qb11)
    CNOT | (qb11, qb10)
    Rx(0.5) | qb11
    H | qb10
    CNOT | (qb10, qb11)
    eng1.flush()
    # mistake in CNOT circuit:
    qb20 = eng2.allocate_qubit()
    qb21 = eng2.allocate_qubit()
    qb22 = eng2.allocate_qubit()
    H | qb20
    Rx(0.6) | qb22
    CNOT | (qb21, qb20)
    CNOT | (qb20, qb21)
    Rx(0.5) | qb21
    H | qb20
    CNOT | (qb20, qb21)
    eng2.flush()
    # test other branch to fail
    qb30 = eng3.allocate_qubit()  # noqa: F841
    qb31 = eng3.allocate_qubit()  # noqa: F841
    qb32 = eng3.allocate_qubit()  # noqa: F841
    eng3.flush()
    assert compare_engine0 == compare_engine1
    assert compare_engine1 != compare_engine2
    assert compare_engine1 != compare_engine3
    assert not compare_engine0 == DummyEngine()

def test_dummy_engine():
    dummy_eng = _testengine.DummyEngine(save_commands=True)
    eng = MainEngine(backend=dummy_eng, engine_list=[])
    assert dummy_eng.is_available("Anything")
    qubit = eng.allocate_qubit()
    H | qubit
    eng.flush()
    assert len(dummy_eng.received_commands) == 3
    assert dummy_eng.received_commands[0].gate == Allocate
    assert dummy_eng.received_commands[1].gate == H
    assert dummy_eng.received_commands[2].gate == FlushGate()