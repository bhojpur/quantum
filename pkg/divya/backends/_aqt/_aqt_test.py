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

"""Tests for divya.backends._aqt._aqt.py."""

import math

import pytest

from divya import MainEngine
from divya.backends._aqt import _aqt
from divya.cengines import BasicMapperEngine, DummyEngine
from divya.ops import (
    NOT,
    All,
    Allocate,
    Barrier,
    Command,
    Deallocate,
    Entangle,
    Measure,
    Rx,
    Rxx,
    Ry,
    Rz,
    S,
    Sdag,
    T,
    Tdag,
    X,
    Y,
    Z,
)
from divya.types import WeakQubitRef

# Insure that no HTTP request can be made in all tests in this module
@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    monkeypatch.delattr("requests.sessions.Session.request")

@pytest.mark.parametrize(
    "single_qubit_gate, is_available",
    [
        (X, False),
        (Y, False),
        (Z, False),
        (T, False),
        (Tdag, False),
        (S, False),
        (Sdag, False),
        (Allocate, True),
        (Deallocate, True),
        (Measure, True),
        (NOT, False),
        (Rx(0.5), True),
        (Ry(0.5), True),
        (Rz(0.5), False),
        (Rxx(0.5), True),
        (Barrier, True),
        (Entangle, False),
    ],
)
def test_aqt_backend_is_available(single_qubit_gate, is_available):
    eng = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])
    qubit1 = eng.allocate_qubit()
    aqt_backend = _aqt.AQTBackend()
    cmd = Command(eng, single_qubit_gate, (qubit1,))
    assert aqt_backend.is_available(cmd) == is_available


@pytest.mark.parametrize("num_ctrl_qubits, is_available", [(0, True), (1, False), (2, False), (3, False)])
def test_aqt_backend_is_available_control_not(num_ctrl_qubits, is_available):
    eng = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])
    qubit1 = eng.allocate_qubit()
    qureg = eng.allocate_qureg(num_ctrl_qubits)
    aqt_backend = _aqt.AQTBackend()
    cmd = Command(eng, Rx(0.5), (qubit1,), controls=qureg)
    assert aqt_backend.is_available(cmd) == is_available
    cmd = Command(eng, Rxx(0.5), (qubit1,), controls=qureg)
    assert aqt_backend.is_available(cmd) == is_available

def test_aqt_backend_init():
    backend = _aqt.AQTBackend(verbose=True, use_hardware=True)
    assert len(backend._circuit) == 0

def test_aqt_empty_circuit():
    backend = _aqt.AQTBackend(verbose=True)
    eng = MainEngine(backend=backend)
    eng.flush()

def test_aqt_invalid_command():
    backend = _aqt.AQTBackend(verbose=True)

    qb = WeakQubitRef(None, 1)
    cmd = Command(None, gate=S, qubits=[(qb,)])
    with pytest.raises(Exception):
        backend.receive([cmd])

def test_aqt_sent_error(monkeypatch):
    # patch send
    def mock_send(*args, **kwargs):
        raise TypeError

    monkeypatch.setattr(_aqt, "send", mock_send)

    backend = _aqt.AQTBackend(verbose=True)
    eng = MainEngine(backend=backend)
    qubit = eng.allocate_qubit()
    Rx(0.5) | qubit
    with pytest.raises(Exception):
        qubit[0].__del__()
        eng.flush()
    # atexit sends another FlushGate, therefore we remove the backend:
    dummy = DummyEngine()
    dummy.is_last_engine = True
    eng.next_engine = dummy

def test_aqt_too_many_runs():
    backend = _aqt.AQTBackend(num_runs=300, verbose=True)
    eng = MainEngine(backend=backend, engine_list=[])
    with pytest.raises(Exception):
        qubit = eng.allocate_qubit()
        Rx(math.pi / 2) | qubit
        eng.flush()

    # Avoid exception at deletion
    backend._num_runs = 1
    backend._circuit = []

def test_aqt_retrieve(monkeypatch):
    # patch send
    def mock_retrieve(*args, **kwargs):
        return [0, 6, 0, 6, 0, 0, 0, 6, 0, 6]

    monkeypatch.setattr(_aqt, "retrieve", mock_retrieve)
    backend = _aqt.AQTBackend(retrieve_execution="a3877d18-314f-46c9-86e7-316bc4dbe968", verbose=True)

    eng = MainEngine(backend=backend, engine_list=[])
    unused_qubit = eng.allocate_qubit()
    qureg = eng.allocate_qureg(2)
    # entangle the qureg
    Ry(math.pi / 2) | qureg[0]
    Rx(math.pi / 2) | qureg[0]
    Rx(math.pi / 2) | qureg[0]
    Ry(math.pi / 2) | qureg[0]
    Rxx(math.pi / 2) | (qureg[0], qureg[1])
    Rx(7 * math.pi / 2) | qureg[0]
    Ry(7 * math.pi / 2) | qureg[0]
    Rx(7 * math.pi / 2) | qureg[1]
    del unused_qubit
    # measure; should be all-0 or all-1
    All(Measure) | qureg
    # run the circuit
    eng.flush()
    prob_dict = eng.backend.get_probabilities([qureg[0], qureg[1]])
    assert prob_dict['11'] == pytest.approx(0.4)
    assert prob_dict['00'] == pytest.approx(0.6)

    # Unknown qubit and no mapper
    invalid_qubit = [WeakQubitRef(eng, 10)]
    with pytest.raises(RuntimeError):
        eng.backend.get_probabilities(invalid_qubit)

def test_aqt_backend_functional_test(monkeypatch):
    correct_info = {
        'circuit': '[["Y", 0.5, [1]], ["X", 0.5, [1]], ["X", 0.5, [1]], '
        '["Y", 0.5, [1]], ["MS", 0.5, [1, 2]], ["X", 3.5, [1]], '
        '["Y", 3.5, [1]], ["X", 3.5, [2]]]',
        'nq': 3,
        'shots': 10,
        'backend': {'name': 'simulator'},
    }

    def mock_send(*args, **kwargs):
        assert args[0] == correct_info
        return [0, 6, 0, 6, 0, 0, 0, 6, 0, 6]

    monkeypatch.setattr(_aqt, "send", mock_send)

    backend = _aqt.AQTBackend(verbose=True, num_runs=10)
    # no circuit has been executed -> raises exception
    with pytest.raises(RuntimeError):
        backend.get_probabilities([])

    mapper = BasicMapperEngine()
    res = {}
    for i in range(4):
        res[i] = i
    mapper.current_mapping = res

    eng = MainEngine(backend=backend, engine_list=[mapper])

    unused_qubit = eng.allocate_qubit()
    qureg = eng.allocate_qureg(2)
    # entangle the qureg
    Ry(math.pi / 2) | qureg[0]
    Rx(math.pi / 2) | qureg[0]
    Rx(math.pi / 2) | qureg[0]
    Ry(math.pi / 2) | qureg[0]
    Rxx(math.pi / 2) | (qureg[0], qureg[1])
    Rx(7 * math.pi / 2) | qureg[0]
    Ry(7 * math.pi / 2) | qureg[0]
    Rx(7 * math.pi / 2) | qureg[1]
    All(Barrier) | qureg
    del unused_qubit
    # measure; should be all-0 or all-1
    All(Measure) | qureg
    # run the circuit
    eng.flush()
    prob_dict = eng.backend.get_probabilities([qureg[0], qureg[1]])
    assert prob_dict['11'] == pytest.approx(0.4)
    assert prob_dict['00'] == pytest.approx(0.6)

    # Unknown qubit and no mapper
    invalid_qubit = [WeakQubitRef(eng, 10)]
    with pytest.raises(RuntimeError):
        eng.backend.get_probabilities(invalid_qubit)

    with pytest.raises(RuntimeError):
        eng.backend.get_probabilities(eng.allocate_qubit())