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

"""Tests for divya.meta._control.py"""
import pytest

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.meta import (
    Compute,
    ComputeTag,
    DirtyQubitTag,
    Uncompute,
    UncomputeTag,
    _control,
)
from divya.ops import Command, CtrlAll, H, IncompatibleControlState, Rx, X
from divya.types import WeakQubitRef

def test_canonical_representation():
    assert _control.canonical_ctrl_state(0, 0) == ''
    for num_qubits in range(4):
        assert _control.canonical_ctrl_state(0, num_qubits) == '0' * num_qubits

    num_qubits = 4
    for i in range(2**num_qubits):
        state = '{0:0b}'.format(i).zfill(num_qubits)
        assert _control.canonical_ctrl_state(i, num_qubits) == state[::-1]
        assert _control.canonical_ctrl_state(state, num_qubits) == state

    for num_qubits in range(10):
        assert _control.canonical_ctrl_state(CtrlAll.Zero, num_qubits) == '0' * num_qubits
        assert _control.canonical_ctrl_state(CtrlAll.One, num_qubits) == '1' * num_qubits

    with pytest.raises(TypeError):
        _control.canonical_ctrl_state(1.1, 2)

    with pytest.raises(ValueError):
        _control.canonical_ctrl_state('1', 2)

    with pytest.raises(ValueError):
        _control.canonical_ctrl_state('11111', 2)

    with pytest.raises(ValueError):
        _control.canonical_ctrl_state('1a', 2)

    with pytest.raises(ValueError):
        _control.canonical_ctrl_state(4, 2)


def test_has_negative_control():
    qubit0 = WeakQubitRef(None, 0)
    qubit1 = WeakQubitRef(None, 0)
    qubit2 = WeakQubitRef(None, 0)
    qubit3 = WeakQubitRef(None, 0)
    assert not _control.has_negative_control(Command(None, H, ([qubit0],)))
    assert not _control.has_negative_control(Command(None, H, ([qubit0],), [qubit1]))
    assert not _control.has_negative_control(Command(None, H, ([qubit0],), [qubit1], control_state=CtrlAll.One))
    assert _control.has_negative_control(Command(None, H, ([qubit0],), [qubit1], control_state=CtrlAll.Zero))
    assert _control.has_negative_control(
        Command(None, H, ([qubit0],), [qubit1, qubit2, qubit3], control_state=CtrlAll.Zero)
    )
    assert not _control.has_negative_control(
        Command(None, H, ([qubit0],), [qubit1, qubit2, qubit3], control_state='111')
    )
    assert _control.has_negative_control(Command(None, H, ([qubit0],), [qubit1, qubit2, qubit3], control_state='101'))

def test_control_engine_has_compute_tag():
    eng = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])
    qubit = eng.allocate_qubit()
    test_cmd0 = Command(eng, H, (qubit,))
    test_cmd1 = Command(eng, H, (qubit,))
    test_cmd2 = Command(eng, H, (qubit,))
    test_cmd0.tags = [DirtyQubitTag(), ComputeTag(), DirtyQubitTag()]
    test_cmd1.tags = [DirtyQubitTag(), UncomputeTag(), DirtyQubitTag()]
    test_cmd2.tags = [DirtyQubitTag()]
    assert _control._has_compute_uncompute_tag(test_cmd0)
    assert _control._has_compute_uncompute_tag(test_cmd1)
    assert not _control._has_compute_uncompute_tag(test_cmd2)

def test_control():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[DummyEngine()])
    qureg = eng.allocate_qureg(2)
    with _control.Control(eng, qureg):
        qubit = eng.allocate_qubit()
        with Compute(eng):
            Rx(0.5) | qubit
        H | qubit
        Uncompute(eng)
    with _control.Control(eng, qureg[0]):
        H | qubit
    eng.flush()
    assert len(backend.received_commands) == 8
    assert len(backend.received_commands[0].control_qubits) == 0
    assert len(backend.received_commands[1].control_qubits) == 0
    assert len(backend.received_commands[2].control_qubits) == 0
    assert len(backend.received_commands[3].control_qubits) == 0
    assert len(backend.received_commands[4].control_qubits) == 2
    assert len(backend.received_commands[5].control_qubits) == 0
    assert len(backend.received_commands[6].control_qubits) == 1
    assert len(backend.received_commands[7].control_qubits) == 0
    assert backend.received_commands[4].control_qubits[0].id == qureg[0].id
    assert backend.received_commands[4].control_qubits[1].id == qureg[1].id
    assert backend.received_commands[6].control_qubits[0].id == qureg[0].id

    with pytest.raises(TypeError):
        _control.Control(eng, (qureg[0], qureg[1]))

def test_control_state():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[DummyEngine()])

    qureg = eng.allocate_qureg(3)
    xreg = eng.allocate_qureg(3)
    X | qureg[1]
    with _control.Control(eng, qureg[0], '0'):
        with Compute(eng):
            X | xreg[0]

        X | xreg[1]
        Uncompute(eng)

    with _control.Control(eng, qureg[1:], 2):
        X | xreg[2]
    eng.flush()

    assert len(backend.received_commands) == 6 + 5 + 1
    assert len(backend.received_commands[0].control_qubits) == 0
    assert len(backend.received_commands[1].control_qubits) == 0
    assert len(backend.received_commands[2].control_qubits) == 0
    assert len(backend.received_commands[3].control_qubits) == 0
    assert len(backend.received_commands[4].control_qubits) == 0
    assert len(backend.received_commands[5].control_qubits) == 0

    assert len(backend.received_commands[6].control_qubits) == 0
    assert len(backend.received_commands[7].control_qubits) == 0
    assert len(backend.received_commands[8].control_qubits) == 1
    assert len(backend.received_commands[9].control_qubits) == 0
    assert len(backend.received_commands[10].control_qubits) == 2

    assert len(backend.received_commands[11].control_qubits) == 0

    assert backend.received_commands[8].control_qubits[0].id == qureg[0].id
    assert backend.received_commands[8].control_state == '0'
    assert backend.received_commands[10].control_qubits[0].id == qureg[1].id
    assert backend.received_commands[10].control_qubits[1].id == qureg[2].id
    assert backend.received_commands[10].control_state == '01'

    assert _control.has_negative_control(backend.received_commands[8])
    assert _control.has_negative_control(backend.received_commands[10])

def test_control_state_contradiction():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[DummyEngine()])
    qureg = eng.allocate_qureg(1)
    with pytest.raises(IncompatibleControlState):
        with _control.Control(eng, qureg[0], '0'):
            qubit = eng.allocate_qubit()
            with _control.Control(eng, qureg[0], '1'):
                H | qubit
    eng.flush()