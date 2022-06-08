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

"""Tests for divya.cengines._ibm5qubitmapper.py."""

import pytest

from divya import MainEngine
from divya.backends import IBMBackend
from divya.cengines import DummyEngine, SwapAndCNOTFlipper, _ibm5qubitmapper
from divya.ops import CNOT, All, H

def test_ibm5qubitmapper_is_available(monkeypatch):
    # Test that IBM5QubitMapper calls IBMBackend if gate is available.
    def mock_send(*args, **kwargs):
        return "Yes"

    monkeypatch.setattr(_ibm5qubitmapper.IBMBackend, "is_available", mock_send)
    mapper = _ibm5qubitmapper.IBM5QubitMapper()
    assert mapper.is_available("TestCommand") == "Yes"

def test_ibm5qubitmapper_invalid_circuit():
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[_ibm5qubitmapper.IBM5QubitMapper(connections=connectivity)],
    )
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    qb3 = eng.allocate_qubit()
    CNOT | (qb1, qb2)
    CNOT | (qb0, qb1)
    CNOT | (qb0, qb2)
    CNOT | (qb3, qb1)
    with pytest.raises(Exception):
        CNOT | (qb3, qb2)
        eng.flush()

def test_ibm5qubitmapper_valid_circuit1():
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[_ibm5qubitmapper.IBM5QubitMapper(connections=connectivity)],
    )
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    qb3 = eng.allocate_qubit()
    qb4 = eng.allocate_qubit()
    CNOT | (qb0, qb1)
    CNOT | (qb0, qb2)
    CNOT | (qb0, qb3)
    CNOT | (qb0, qb4)
    CNOT | (qb1, qb2)
    CNOT | (qb3, qb4)
    CNOT | (qb4, qb3)
    eng.flush()

def test_ibm5qubitmapper_valid_circuit2():
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[_ibm5qubitmapper.IBM5QubitMapper(connections=connectivity)],
    )
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    qb3 = eng.allocate_qubit()
    qb4 = eng.allocate_qubit()
    CNOT | (qb3, qb1)
    CNOT | (qb3, qb2)
    CNOT | (qb3, qb0)
    CNOT | (qb3, qb4)
    CNOT | (qb1, qb2)
    CNOT | (qb0, qb4)
    CNOT | (qb2, qb1)
    eng.flush()

def test_ibm5qubitmapper_valid_circuit2_ibmqx4():
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    backend = DummyEngine(save_commands=True)

    class FakeIBMBackend(IBMBackend):
        pass

    fake = FakeIBMBackend(device='ibmqx4', use_hardware=True)
    fake.receive = backend.receive
    fake.is_available = backend.is_available
    backend.is_last_engine = True

    eng = MainEngine(
        backend=fake,
        engine_list=[_ibm5qubitmapper.IBM5QubitMapper(connections=connectivity)],
    )
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    qb3 = eng.allocate_qubit()
    qb4 = eng.allocate_qubit()
    CNOT | (qb3, qb1)
    CNOT | (qb3, qb2)
    CNOT | (qb3, qb0)
    CNOT | (qb3, qb4)
    CNOT | (qb1, qb2)
    CNOT | (qb0, qb4)
    CNOT | (qb2, qb1)
    eng.flush()

def test_ibm5qubitmapper_optimizeifpossible():
    backend = DummyEngine(save_commands=True)
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    eng = MainEngine(
        backend=backend,
        engine_list=[
            _ibm5qubitmapper.IBM5QubitMapper(connections=connectivity),
            SwapAndCNOTFlipper(connectivity),
        ],
    )
    qb0 = eng.allocate_qubit()  # noqa: F841
    qb1 = eng.allocate_qubit()
    qb2 = eng.allocate_qubit()
    qb3 = eng.allocate_qubit()  # noqa: F841
    CNOT | (qb1, qb2)
    CNOT | (qb2, qb1)
    CNOT | (qb1, qb2)

    eng.flush()

    hadamard_count = 0
    for cmd in backend.received_commands:
        if cmd.gate == H:
            hadamard_count += 1

    assert hadamard_count == 4
    backend.received_commands = []

    CNOT | (qb2, qb1)
    CNOT | (qb1, qb2)
    CNOT | (qb2, qb1)

    eng.flush()

    hadamard_count = 0
    for cmd in backend.received_commands:
        if cmd.gate == H:
            hadamard_count += 1

    assert hadamard_count == 4

def test_ibm5qubitmapper_toomanyqubits():
    backend = DummyEngine(save_commands=True)
    connectivity = {(2, 1), (4, 2), (2, 0), (3, 2), (3, 4), (1, 0)}
    eng = MainEngine(
        backend=backend,
        engine_list=[
            _ibm5qubitmapper.IBM5QubitMapper(),
            SwapAndCNOTFlipper(connectivity),
        ],
    )
    qubits = eng.allocate_qureg(6)
    All(H) | qubits
    CNOT | (qubits[0], qubits[1])
    with pytest.raises(RuntimeError):
        eng.flush()