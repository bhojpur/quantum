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

"""
Tests for decompositions rules (using the Simulator).
"""

import pytest

from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
    MainEngine,
)
from divya.meta import Control
from divya.ops import (
    All,
    ClassicalInstructionGate,
    CRz,
    Entangle,
    H,
    Measure,
    Ph,
    R,
    Rz,
    T,
    Tdag,
    Toffoli,
    X,
)
from divya.setups.decompositions import (
    crz2cxandrz,
    entangle,
    globalphase,
    ph2r,
    r2rzandph,
    toffoli2cnotandtgate,
)

def low_level_gates(eng, cmd):
    g = cmd.gate
    if isinstance(g, ClassicalInstructionGate):
        return True
    if len(cmd.control_qubits) == 0:
        if g == T or g == Tdag or g == H or isinstance(g, Rz) or isinstance(g, Ph):
            return True
    else:
        if len(cmd.control_qubits) == 1 and cmd.gate == X:
            return True
    return False

def test_entangle():
    rule_set = DecompositionRuleSet(modules=[entangle])
    sim = Simulator()
    eng = MainEngine(sim, [AutoReplacer(rule_set), InstructionFilter(low_level_gates)])
    qureg = eng.allocate_qureg(4)
    Entangle | qureg

    assert 0.5 == pytest.approx(abs(sim.cheat()[1][0]) ** 2)
    assert 0.5 == pytest.approx(abs(sim.cheat()[1][-1]) ** 2)

    All(Measure) | qureg

def low_level_gates_noglobalphase(eng, cmd):
    return low_level_gates(eng, cmd) and not isinstance(cmd.gate, Ph) and not isinstance(cmd.gate, R)

def test_globalphase():
    rule_set = DecompositionRuleSet(modules=[globalphase, r2rzandph])
    dummy = DummyEngine(save_commands=True)
    eng = MainEngine(
        dummy,
        [AutoReplacer(rule_set), InstructionFilter(low_level_gates_noglobalphase)],
    )

    qubit = eng.allocate_qubit()
    R(1.2) | qubit

    rz_count = 0
    for cmd in dummy.received_commands:
        assert not isinstance(cmd.gate, R)
        if isinstance(cmd.gate, Rz):
            rz_count += 1
            assert cmd.gate == Rz(1.2)

    assert rz_count == 1

def run_circuit(eng):
    qureg = eng.allocate_qureg(4)
    All(H) | qureg
    CRz(3.0) | (qureg[0], qureg[1])
    Toffoli | (qureg[1], qureg[2], qureg[3])

    with Control(eng, qureg[0:2]):
        Ph(1.43) | qureg[2]
    return qureg

def test_gate_decompositions():
    sim = Simulator()
    eng = MainEngine(sim, [])
    rule_set = DecompositionRuleSet(modules=[r2rzandph, crz2cxandrz, toffoli2cnotandtgate, ph2r])

    qureg = run_circuit(eng)

    sim2 = Simulator()
    eng_lowlevel = MainEngine(sim2, [AutoReplacer(rule_set), InstructionFilter(low_level_gates)])
    qureg2 = run_circuit(eng_lowlevel)

    for i in range(len(sim.cheat()[1])):
        assert sim.cheat()[1][i] == pytest.approx(sim2.cheat()[1][i])

    All(Measure) | qureg
    All(Measure) | qureg2