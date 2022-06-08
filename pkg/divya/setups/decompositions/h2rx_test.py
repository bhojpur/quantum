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

"Tests for divya.setups.decompositions.h2rx.py"

import pytest

from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
)
from divya.meta import Control
from divya.ops import H, HGate, Measure

from . import h2rx

def test_recognize_correct_gates():
    """Test that recognize_HNoCtrl recognizes ctrl qubits"""
    saving_backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=saving_backend)
    qubit = eng.allocate_qubit()
    ctrl_qubit = eng.allocate_qubit()
    eng.flush()
    H | qubit
    with Control(eng, ctrl_qubit):
        H | qubit
    eng.flush(deallocate_qubits=True)
    assert h2rx._recognize_HNoCtrl(saving_backend.received_commands[3])
    assert not h2rx._recognize_HNoCtrl(saving_backend.received_commands[4])

def h_decomp_gates(eng, cmd):
    """Test that cmd.gate is a gate of class HGate"""
    g = cmd.gate
    if isinstance(g, HGate):  # H is just a shortcut to HGate
        return False
    else:
        return True

# ------------test_decomposition function-------------#
# Creates two engines, correct_eng and test_eng.
# correct_eng implements H gate.
# test_eng implements the decomposition of the H gate.
# correct_qb and test_qb represent results of these two engines, respectively.
#
# The decomposition in this case only produces the same state as H up to a
# global phase.
# test_vector and correct_vector represent the final wave states of correct_qb
# and test_qb.
# The dot product of correct_vector and test_vector should have absolute value
# 1, if the two vectors are the same up to a global phase.

def test_decomposition():
    """Test that this decomposition of H produces correct amplitudes

    Function tests each DecompositionRule in
    h2rx.all_defined_decomposition_rules
    """
    decomposition_rule_list = h2rx.all_defined_decomposition_rules
    for rule in decomposition_rule_list:
        for basis_state_index in range(2):
            basis_state = [0] * 2
            basis_state[basis_state_index] = 1.0

            correct_dummy_eng = DummyEngine(save_commands=True)
            correct_eng = MainEngine(backend=Simulator(), engine_list=[correct_dummy_eng])

            rule_set = DecompositionRuleSet(rules=[rule])
            test_dummy_eng = DummyEngine(save_commands=True)
            test_eng = MainEngine(
                backend=Simulator(),
                engine_list=[
                    AutoReplacer(rule_set),
                    InstructionFilter(h_decomp_gates),
                    test_dummy_eng,
                ],
            )

            correct_qb = correct_eng.allocate_qubit()
            correct_eng.flush()
            test_qb = test_eng.allocate_qubit()
            test_eng.flush()

            correct_eng.backend.set_wavefunction(basis_state, correct_qb)
            test_eng.backend.set_wavefunction(basis_state, test_qb)

            H | correct_qb
            H | test_qb

            correct_eng.flush()
            test_eng.flush()

            assert H in (cmd.gate for cmd in correct_dummy_eng.received_commands)
            assert H not in (cmd.gate for cmd in test_dummy_eng.received_commands)

            assert correct_eng.backend.cheat()[1] == pytest.approx(test_eng.backend.cheat()[1], rel=1e-12, abs=1e-12)

            Measure | test_qb
            Measure | correct_qb