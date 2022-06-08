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

"""Tests for divya.meta._dagger.py"""

import types

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.meta import DirtyQubitTag, _dagger
from divya.ops import CNOT, Allocate, Deallocate, H, Rx, X

def test_dagger_with_dirty_qubits():
    backend = DummyEngine(save_commands=True)

    def allow_dirty_qubits(self, meta_tag):
        return meta_tag == DirtyQubitTag

    backend.is_meta_tag_handler = types.MethodType(allow_dirty_qubits, backend)
    eng = MainEngine(backend=backend, engine_list=[DummyEngine()])
    qubit = eng.allocate_qubit()
    with _dagger.Dagger(eng):
        ancilla = eng.allocate_qubit(dirty=True)
        Rx(0.6) | ancilla
        CNOT | (ancilla, qubit)
        H | qubit
        Rx(-0.6) | ancilla
        del ancilla[0]
    eng.flush(deallocate_qubits=True)
    assert len(backend.received_commands) == 9
    assert backend.received_commands[0].gate == Allocate
    assert backend.received_commands[1].gate == Allocate
    assert backend.received_commands[2].gate == Rx(0.6)
    assert backend.received_commands[3].gate == H
    assert backend.received_commands[4].gate == X
    assert backend.received_commands[5].gate == Rx(-0.6)
    assert backend.received_commands[6].gate == Deallocate
    assert backend.received_commands[7].gate == Deallocate
    assert backend.received_commands[1].tags == [DirtyQubitTag()]
    assert backend.received_commands[6].tags == [DirtyQubitTag()]

def test_dagger_qubit_management_error():
    eng = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])
    with pytest.raises(_dagger.QubitManagementError):
        with _dagger.Dagger(eng):
            ancilla = eng.allocate_qubit()  # noqa: F841

def test_dagger_raises_only_single_error():
    eng = MainEngine(backend=DummyEngine(), engine_list=[])
    # Tests that QubitManagementError is not sent in addition
    with pytest.raises(RuntimeError):
        with _dagger.Dagger(eng):
            ancilla = eng.allocate_qubit()  # noqa: F841
            raise RuntimeError