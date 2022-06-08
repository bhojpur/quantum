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
Tests for divya.backends._resource.py.
"""

import pytest

from divya.backends import ResourceCounter
from divya.cengines import DummyEngine, MainEngine, NotYetMeasuredError
from divya.meta import LogicalQubitIDTag
from divya.ops import CNOT, QFT, All, Allocate, Command, H, Measure, Rz, Rzz, X
from divya.types import WeakQubitRef

class MockEngine(object):
    def is_available(self, cmd):
        return False

def test_resource_counter_isavailable():
    resource_counter = ResourceCounter()
    resource_counter.next_engine = MockEngine()
    assert not resource_counter.is_available("test")
    resource_counter.next_engine = None
    resource_counter.is_last_engine = True

    assert resource_counter.is_available("test")

def test_resource_counter_measurement():
    eng = MainEngine(ResourceCounter(), [])
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

def test_resource_counter():
    resource_counter = ResourceCounter()
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend, [resource_counter])

    qubit1 = eng.allocate_qubit()
    qubit2 = eng.allocate_qubit()
    H | qubit1
    X | qubit2
    del qubit2

    qubit3 = eng.allocate_qubit()
    CNOT | (qubit1, qubit3)
    Rz(0.1) | qubit1
    Rz(0.3) | qubit1
    Rzz(0.5) | qubit1

    All(Measure) | qubit1 + qubit3

    with pytest.raises(NotYetMeasuredError):
        int(qubit1)

    assert resource_counter.max_width == 2
    assert resource_counter.depth_of_dag == 6

    str_repr = str(resource_counter)
    assert str_repr.count(" HGate : 1") == 1
    assert str_repr.count(" XGate : 1") == 1
    assert str_repr.count(" CXGate : 1") == 1
    assert str_repr.count(" Rz : 2") == 1
    assert str_repr.count(" AllocateQubitGate : 3") == 1
    assert str_repr.count(" DeallocateQubitGate : 1") == 1

    assert str_repr.count(" H : 1") == 1
    assert str_repr.count(" X : 1") == 1
    assert str_repr.count(" CX : 1") == 1
    assert str_repr.count(" Rz(0.1) : 1") == 1
    assert str_repr.count(" Rz(0.3) : 1") == 1
    assert str_repr.count(" Allocate : 3") == 1
    assert str_repr.count(" Deallocate : 1") == 1

    sent_gates = [cmd.gate for cmd in backend.received_commands]
    assert sent_gates.count(H) == 1
    assert sent_gates.count(X) == 2
    assert sent_gates.count(Measure) == 2

def test_resource_counter_str_when_empty():
    assert isinstance(str(ResourceCounter()), str)

def test_resource_counter_depth_of_dag():
    resource_counter = ResourceCounter()
    eng = MainEngine(resource_counter, [])
    assert resource_counter.depth_of_dag == 0
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    QFT | qb0 + qb1 + qb2
    assert resource_counter.depth_of_dag == 1
    H | qb0
    H | qb0
    assert resource_counter.depth_of_dag == 3
    CNOT | (qb0, qb1)
    X | qb1
    assert resource_counter.depth_of_dag == 5
    Measure | qb1
    Measure | qb1
    assert resource_counter.depth_of_dag == 7
    CNOT | (qb1, qb2)
    Measure | qb2
    assert resource_counter.depth_of_dag == 9
    qb1[0].__del__()
    qb2[0].__del__()
    assert resource_counter.depth_of_dag == 9
    qb0[0].__del__()
    assert resource_counter.depth_of_dag == 9