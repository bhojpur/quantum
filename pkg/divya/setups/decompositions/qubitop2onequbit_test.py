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

import cmath

import pytest

import divya.setups.decompositions.qubitop2onequbit as qubitop2onequbit
from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
)
from divya.meta import Control
from divya.ops import All, Command, Measure, Ph, QubitOperator, X, Y, Z
from divya.types import WeakQubitRef

def test_recognize():
    saving_backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=saving_backend, engine_list=[])
    ctrl_qureg = eng.allocate_qureg(2)
    qureg = eng.allocate_qureg(2)
    with Control(eng, ctrl_qureg):
        QubitOperator("X0 Y1") | qureg
    with Control(eng, ctrl_qureg[0]):
        QubitOperator("X0 Y1") | qureg
    eng.flush()
    cmd0 = saving_backend.received_commands[4]
    cmd1 = saving_backend.received_commands[5]
    assert not qubitop2onequbit._recognize_qubitop(cmd0)
    assert qubitop2onequbit._recognize_qubitop(cmd1)

def _decomp_gates(eng, cmd):
    if isinstance(cmd.gate, QubitOperator):
        return False
    else:
        return True

def test_qubitop2singlequbit_invalid():
    qb0 = WeakQubitRef(None, idx=0)
    qb1 = WeakQubitRef(None, idx=1)
    with pytest.raises(ValueError):
        qubitop2onequbit._decompose_qubitop(Command(None, QubitOperator(), ([qb0], [qb1])))

def test_qubitop2singlequbit():
    num_qubits = 4
    random_initial_state = [0.2 + 0.1 * x * cmath.exp(0.1j + 0.2j * x) for x in range(2 ** (num_qubits + 1))]
    rule_set = DecompositionRuleSet(modules=[qubitop2onequbit])
    test_eng = MainEngine(
        backend=Simulator(),
        engine_list=[AutoReplacer(rule_set), InstructionFilter(_decomp_gates)],
    )
    test_qureg = test_eng.allocate_qureg(num_qubits)
    test_ctrl_qb = test_eng.allocate_qubit()
    test_eng.flush()
    test_eng.backend.set_wavefunction(random_initial_state, test_qureg + test_ctrl_qb)
    correct_eng = MainEngine()
    correct_qureg = correct_eng.allocate_qureg(num_qubits)
    correct_ctrl_qb = correct_eng.allocate_qubit()
    correct_eng.flush()
    correct_eng.backend.set_wavefunction(random_initial_state, correct_qureg + correct_ctrl_qb)

    qubit_op_0 = QubitOperator("X0 Y1 Z3", -1.0j)
    qubit_op_1 = QubitOperator("Z0 Y1 X3", cmath.exp(0.6j))

    qubit_op_0 | test_qureg
    with Control(test_eng, test_ctrl_qb):
        qubit_op_1 | test_qureg
    test_eng.flush()

    correct_eng.backend.apply_qubit_operator(qubit_op_0, correct_qureg)
    with Control(correct_eng, correct_ctrl_qb):
        Ph(0.6) | correct_qureg[0]
        Z | correct_qureg[0]
        Y | correct_qureg[1]
        X | correct_qureg[3]
    correct_eng.flush()

    for fstate in range(2 ** (num_qubits + 1)):
        binary_state = format(fstate, '0' + str(num_qubits + 1) + 'b')
        test = test_eng.backend.get_amplitude(binary_state, test_qureg + test_ctrl_qb)
        correct = correct_eng.backend.get_amplitude(binary_state, correct_qureg + correct_ctrl_qb)
        assert correct == pytest.approx(test, rel=1e-10, abs=1e-10)

    All(Measure) | correct_qureg + correct_ctrl_qb
    All(Measure) | test_qureg + test_ctrl_qb
    correct_eng.flush()
    test_eng.flush()