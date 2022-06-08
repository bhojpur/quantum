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

"""Tests for divya.setups.decompositions.uniformlycontrolledr2cnot."""

import pytest

import divya.setups.decompositions.uniformlycontrolledr2cnot as ucr2cnot
from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
)
from divya.meta import Compute, Control, Uncompute
from divya.ops import (
    All,
    Measure,
    Ry,
    Rz,
    UniformlyControlledRy,
    UniformlyControlledRz,
    X,
)

def slow_implementation(angles, control_qubits, target_qubit, eng, gate_class):
    """
    Assumption is that control_qubits[0] is lowest order bit
    We apply angles[0] to state |0>
    """
    assert len(angles) == 2 ** len(control_qubits)
    for index in range(2 ** len(control_qubits)):
        with Compute(eng):
            for bit_pos in range(len(control_qubits)):
                if not (index >> bit_pos) & 1:
                    X | control_qubits[bit_pos]
        with Control(eng, control_qubits):
            gate_class(angles[index]) | target_qubit
        Uncompute(eng)

def _decomp_gates(eng, cmd):
    if isinstance(cmd.gate, UniformlyControlledRy) or isinstance(cmd.gate, UniformlyControlledRz):
        return False
    return True

def test_no_control_qubits():
    rule_set = DecompositionRuleSet(modules=[ucr2cnot])
    eng = MainEngine(
        backend=DummyEngine(),
        engine_list=[AutoReplacer(rule_set), InstructionFilter(_decomp_gates)],
    )
    qb = eng.allocate_qubit()
    with pytest.raises(TypeError):
        UniformlyControlledRy([0.1]) | qb

def test_wrong_number_of_angles():
    rule_set = DecompositionRuleSet(modules=[ucr2cnot])
    eng = MainEngine(
        backend=DummyEngine(),
        engine_list=[AutoReplacer(rule_set), InstructionFilter(_decomp_gates)],
    )
    qb = eng.allocate_qubit()
    with pytest.raises(ValueError):
        UniformlyControlledRy([0.1, 0.2]) | ([], qb)

@pytest.mark.parametrize("gate_classes", [(Ry, UniformlyControlledRy), (Rz, UniformlyControlledRz)])
@pytest.mark.parametrize("n", [0, 1, 2, 3, 4])
def test_uniformly_controlled_ry(n, gate_classes):
    random_angles = [
        0.5,
        0.8,
        1.2,
        2.5,
        4.4,
        2.32,
        6.6,
        15.12,
        1,
        2,
        9.54,
        2.1,
        3.1415,
        1.1,
        0.01,
        0.99,
    ]
    angles = random_angles[: 2**n]
    for basis_state_index in range(0, 2 ** (n + 1)):
        basis_state = [0] * 2 ** (n + 1)
        basis_state[basis_state_index] = 1.0
        correct_dummy_eng = DummyEngine(save_commands=True)
        correct_eng = MainEngine(backend=Simulator(), engine_list=[correct_dummy_eng])
        rule_set = DecompositionRuleSet(modules=[ucr2cnot])
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
        correct_qb = correct_eng.allocate_qubit()
        correct_ctrl_qureg = correct_eng.allocate_qureg(n)
        correct_eng.flush()
        test_qb = test_eng.allocate_qubit()
        test_ctrl_qureg = test_eng.allocate_qureg(n)
        test_eng.flush()

        correct_sim.set_wavefunction(basis_state, correct_qb + correct_ctrl_qureg)
        test_sim.set_wavefunction(basis_state, test_qb + test_ctrl_qureg)

        gate_classes[1](angles) | (test_ctrl_qureg, test_qb)
        slow_implementation(
            angles=angles,
            control_qubits=correct_ctrl_qureg,
            target_qubit=correct_qb,
            eng=correct_eng,
            gate_class=gate_classes[0],
        )
        test_eng.flush()
        correct_eng.flush()

        for fstate in range(2 ** (n + 1)):
            binary_state = format(fstate, '0' + str(n + 1) + 'b')
            test = test_sim.get_amplitude(binary_state, test_qb + test_ctrl_qureg)
            correct = correct_sim.get_amplitude(binary_state, correct_qb + correct_ctrl_qureg)
            assert correct == pytest.approx(test, rel=1e-10, abs=1e-10)

        All(Measure) | test_qb + test_ctrl_qureg
        All(Measure) | correct_qb + correct_ctrl_qureg
        test_eng.flush(deallocate_qubits=True)
        correct_eng.flush(deallocate_qubits=True)