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

"""Tests for divya.setups.decompositions.stateprep2cnot."""

import cmath
import math
from copy import deepcopy

import numpy as np
import pytest

import divya
import divya.setups.decompositions.stateprep2cnot as stateprep2cnot
from divya.ops import All, Command, Measure, Ph, Ry, Rz, StatePreparation
from divya.setups import restrictedgateset
from divya.types import WeakQubitRef

def test_invalid_arguments():
    qb0 = WeakQubitRef(engine=None, idx=0)
    qb1 = WeakQubitRef(engine=None, idx=1)
    cmd = Command(None, StatePreparation([0, 1j]), qubits=([qb0], [qb1]))
    with pytest.raises(ValueError):
        stateprep2cnot._decompose_state_preparation(cmd)

def test_wrong_final_state():
    qb0 = WeakQubitRef(engine=None, idx=0)
    qb1 = WeakQubitRef(engine=None, idx=1)
    cmd = Command(None, StatePreparation([0, 1j]), qubits=([qb0, qb1],))
    with pytest.raises(ValueError):
        stateprep2cnot._decompose_state_preparation(cmd)
    cmd2 = Command(None, StatePreparation([0, 0.999j]), qubits=([qb0],))
    with pytest.raises(ValueError):
        stateprep2cnot._decompose_state_preparation(cmd2)

@pytest.mark.parametrize("zeros", [True, False])
@pytest.mark.parametrize("n_qubits", [1, 2, 3, 4])
def test_state_preparation(n_qubits, zeros):
    engine_list = restrictedgateset.get_engine_list(one_qubit_gates=(Ry, Rz, Ph))
    eng = divya.MainEngine(engine_list=engine_list)
    qureg = eng.allocate_qureg(n_qubits)
    eng.flush()

    f_state = [0.2 + 0.1 * x * cmath.exp(0.1j + 0.2j * x) for x in range(2**n_qubits)]
    if zeros:
        for i in range(2 ** (n_qubits - 1)):
            f_state[i] = 0
    norm = 0
    for amplitude in f_state:
        norm += abs(amplitude) ** 2
    f_state = [x / math.sqrt(norm) for x in f_state]

    StatePreparation(f_state) | qureg
    eng.flush()

    wavefunction = deepcopy(eng.backend.cheat()[1])
    # Test that simulator hasn't reordered wavefunction
    mapping = eng.backend.cheat()[0]
    for key in mapping:
        assert mapping[key] == key
    All(Measure) | qureg
    eng.flush()
    assert np.allclose(wavefunction, f_state, rtol=1e-10, atol=1e-10)