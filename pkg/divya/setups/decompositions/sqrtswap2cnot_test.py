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

"""Tests for divya.setups.decompositions.sqrtswap2cnot."""

import pytest

import divya.setups.decompositions.sqrtswap2cnot as sqrtswap2cnot
from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
)
from divya.ops import All, Command, Measure, SqrtSwap
from divya.types import WeakQubitRef

def _decomp_gates(eng, cmd):
    if isinstance(cmd.gate, SqrtSwap.__class__):
        return False
    return True

def test_sqrtswap_invalid():
    qb0 = WeakQubitRef(engine=None, idx=0)
    qb1 = WeakQubitRef(engine=None, idx=1)
    qb2 = WeakQubitRef(engine=None, idx=2)

    with pytest.raises(ValueError):
        sqrtswap2cnot._decompose_sqrtswap(Command(None, SqrtSwap, ([qb0], [qb1], [qb2])))

    with pytest.raises(ValueError):
        sqrtswap2cnot._decompose_sqrtswap(Command(None, SqrtSwap, ([qb0], [qb1, qb2])))

def test_sqrtswap():
    for basis_state in ([1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]):
        correct_dummy_eng = DummyEngine(save_commands=True)
        correct_eng = MainEngine(backend=Simulator(), engine_list=[correct_dummy_eng])
        rule_set = DecompositionRuleSet(modules=[sqrtswap2cnot])
        test_dummy_eng = DummyEngine(save_commands=True)
        test_eng = MainEngine(
            backend=Simulator(),
            engine_list=[
                AutoReplacer(rule_set),
                InstructionFilter(_decomp_gates),
                test_dummy_eng,
            ],
        )
        test_sim = test_eng.backend
        correct_sim = correct_eng.backend
        correct_qureg = correct_eng.allocate_qureg(2)
        correct_eng.flush()
        test_qureg = test_eng.allocate_qureg(2)
        test_eng.flush()

        correct_sim.set_wavefunction(basis_state, correct_qureg)
        test_sim.set_wavefunction(basis_state, test_qureg)

        SqrtSwap | (test_qureg[0], test_qureg[1])
        test_eng.flush()
        SqrtSwap | (correct_qureg[0], correct_qureg[1])
        correct_eng.flush()

        assert len(test_dummy_eng.received_commands) != len(correct_dummy_eng.received_commands)
        for fstate in range(4):
            binary_state = format(fstate, '02b')
            test = test_sim.get_amplitude(binary_state, test_qureg)
            correct = correct_sim.get_amplitude(binary_state, correct_qureg)
            assert correct == pytest.approx(test, rel=1e-10, abs=1e-10)

        All(Measure) | test_qureg
        All(Measure) | correct_qureg
        test_eng.flush(deallocate_qubits=True)
        correct_eng.flush(deallocate_qubits=True)