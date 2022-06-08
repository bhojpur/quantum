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

from divya.backends import Simulator
from divya.backends._ionq._ionq_mapper import BoundedQubitMapper
from divya.cengines import DummyEngine, MainEngine
from divya.meta import LogicalQubitIDTag
from divya.ops import AllocateQubitGate, Command, DeallocateQubitGate
from divya.types import WeakQubitRef

def test_cannot_allocate_past_max():
    mapper = BoundedQubitMapper(1)
    engine = MainEngine(
        DummyEngine(),
        engine_list=[mapper],
        verbose=True,
    )
    engine.allocate_qubit()
    with pytest.raises(RuntimeError) as excinfo:
        engine.allocate_qubit()

    assert str(excinfo.value) == "Cannot allocate more than 1 qubits!"

    # Avoid double error reporting
    mapper.current_mapping = {0: 0, 1: 1}

def test_cannot_reallocate_same_qubit():
    engine = MainEngine(
        Simulator(),
        engine_list=[BoundedQubitMapper(1)],
        verbose=True,
    )
    qureg = engine.allocate_qubit()
    qubit = qureg[0]
    qubit_id = qubit.id
    with pytest.raises(RuntimeError) as excinfo:
        allocate_cmd = Command(
            engine=engine,
            gate=AllocateQubitGate(),
            qubits=([WeakQubitRef(engine=engine, idx=qubit_id)],),
            tags=[LogicalQubitIDTag(qubit_id)],
        )
        engine.send([allocate_cmd])

    assert str(excinfo.value) == "Qubit with id 0 has already been allocated!"

def test_cannot_deallocate_unknown_qubit():
    engine = MainEngine(
        Simulator(),
        engine_list=[BoundedQubitMapper(1)],
        verbose=True,
    )
    qureg = engine.allocate_qubit()
    with pytest.raises(RuntimeError) as excinfo:
        deallocate_cmd = Command(
            engine=engine,
            gate=DeallocateQubitGate(),
            qubits=([WeakQubitRef(engine=engine, idx=1)],),
            tags=[LogicalQubitIDTag(1)],
        )
        engine.send([deallocate_cmd])
    assert str(excinfo.value) == "Cannot deallocate a qubit that is not already allocated!"

    # but we can still deallocate an already allocated one
    engine.deallocate_qubit(qureg[0])
    del qureg
    del engine

def test_cannot_deallocate_same_qubit():
    mapper = BoundedQubitMapper(1)
    engine = MainEngine(
        Simulator(),
        engine_list=[mapper],
        verbose=True,
    )
    qureg = engine.allocate_qubit()
    qubit_id = qureg[0].id
    engine.deallocate_qubit(qureg[0])

    with pytest.raises(RuntimeError) as excinfo:
        deallocate_cmd = Command(
            engine=engine,
            gate=DeallocateQubitGate(),
            qubits=([WeakQubitRef(engine=engine, idx=qubit_id)],),
            tags=[LogicalQubitIDTag(qubit_id)],
        )
        engine.send([deallocate_cmd])

    assert str(excinfo.value) == "Cannot deallocate a qubit that is not already allocated!"

def test_flush_deallocates_all_qubits():
    mapper = BoundedQubitMapper(10)
    engine = MainEngine(
        Simulator(),
        engine_list=[mapper],
        verbose=True,
    )
    # needed to prevent GC from removing qubit refs
    qureg = engine.allocate_qureg(10)
    assert len(mapper.current_mapping.keys()) == 10
    assert len(engine.active_qubits) == 10
    engine.flush()
    # Should still be around after flush
    assert len(engine.active_qubits) == 10
    assert len(mapper.current_mapping.keys()) == 10

    # GC will clean things up
    del qureg
    assert len(engine.active_qubits) == 0
    assert len(mapper.current_mapping.keys()) == 0