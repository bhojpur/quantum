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

"""Tests for divya.cengines._optimize.py."""

import math

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine, _optimize
from divya.ops import (
    CNOT,
    AllocateQubitGate,
    ClassicalInstructionGate,
    FastForwardingGate,
    H,
    Rx,
    Ry,
    X,
)

def test_local_optimizer_init_api_change():
    with pytest.warns(DeprecationWarning):
        tmp = _optimize.LocalOptimizer(m=10)
        assert tmp._cache_size == 10

    local_optimizer = _optimize.LocalOptimizer()
    assert local_optimizer._cache_size == 5

    local_optimizer = _optimize.LocalOptimizer(cache_size=10)
    assert local_optimizer._cache_size == 10

def test_local_optimizer_caching():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that it caches for each qubit 3 gates
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    assert len(backend.received_commands) == 0
    H | qb0
    H | qb1
    CNOT | (qb0, qb1)
    assert len(backend.received_commands) == 0
    Rx(0.5) | qb0
    assert len(backend.received_commands) == 1
    assert backend.received_commands[0].gate == AllocateQubitGate()
    H | qb0
    assert len(backend.received_commands) == 2
    assert backend.received_commands[1].gate == H
    # Another gate on qb0 means it needs to send CNOT but clear pipeline of qb1
    Rx(0.6) | qb0
    for cmd in backend.received_commands:
        print(cmd)
    assert len(backend.received_commands) == 5
    assert backend.received_commands[2].gate == AllocateQubitGate()
    assert backend.received_commands[3].gate == H
    assert backend.received_commands[3].qubits[0][0].id == qb1[0].id
    assert backend.received_commands[4].gate == X
    assert backend.received_commands[4].control_qubits[0].id == qb0[0].id
    assert backend.received_commands[4].qubits[0][0].id == qb1[0].id

def test_local_optimizer_flush_gate():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that it caches for each qubit 3 gates
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    H | qb0
    H | qb1
    assert len(backend.received_commands) == 0
    eng.flush()
    # Two allocate gates, two H gates and one flush gate
    assert len(backend.received_commands) == 5

def test_local_optimizer_fast_forwarding_gate():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that FastForwardingGate (e.g. Deallocate) flushes that qb0 pipeline
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    H | qb0
    H | qb1
    assert len(backend.received_commands) == 0
    qb0[0].__del__()
    # As Deallocate gate is a FastForwardingGate, we should get gates of qb0
    assert len(backend.received_commands) == 3

def test_local_optimizer_cancel_inverse():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that it cancels inverses (H, CNOT are self-inverse)
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    assert len(backend.received_commands) == 0
    for _ in range(11):
        H | qb0
    assert len(backend.received_commands) == 0
    for _ in range(11):
        CNOT | (qb0, qb1)
    assert len(backend.received_commands) == 0
    eng.flush()
    received_commands = []
    # Remove Allocate and Deallocate gates
    for cmd in backend.received_commands:
        if not (isinstance(cmd.gate, FastForwardingGate) or isinstance(cmd.gate, ClassicalInstructionGate)):
            received_commands.append(cmd)
    assert len(received_commands) == 2
    assert received_commands[0].gate == H
    assert received_commands[0].qubits[0][0].id == qb0[0].id
    assert received_commands[1].gate == X
    assert received_commands[1].qubits[0][0].id == qb1[0].id
    assert received_commands[1].control_qubits[0].id == qb0[0].id

def test_local_optimizer_mergeable_gates():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that it merges mergeable gates such as Rx
    qb0 = eng.allocate_qubit()
    for _ in range(10):
        Rx(0.5) | qb0
    assert len(backend.received_commands) == 0
    eng.flush()
    # Expect allocate, one Rx gate, and flush gate
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == Rx(10 * 0.5)

def test_local_optimizer_identity_gates():
    local_optimizer = _optimize.LocalOptimizer(cache_size=4)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[local_optimizer])
    # Test that it merges mergeable gates such as Rx
    qb0 = eng.allocate_qubit()
    for _ in range(10):
        Rx(0.0) | qb0
        Ry(0.0) | qb0
        Rx(4 * math.pi) | qb0
        Ry(4 * math.pi) | qb0
    Rx(0.5) | qb0
    assert len(backend.received_commands) == 0
    eng.flush()
    # Expect allocate, one Rx gate, and flush gate
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == Rx(0.5)