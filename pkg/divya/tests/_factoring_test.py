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

import pytest

import divya.libs.math
import divya.setups.decompositions
from divya.backends._sim._simulator_test import sim
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    InstructionFilter,
    LocalOptimizer,
    MainEngine,
    TagRemover,
)
from divya.libs.math import MultiplyByConstantModN
from divya.meta import Control
from divya.ops import QFT, All, BasicMathGate, H, Measure, Swap, X, get_inverse

rule_set = DecompositionRuleSet(modules=(divya.libs.math, divya.setups.decompositions))

assert sim  # Asserts to tools that the fixture import is used.

def high_level_gates(eng, cmd):
    g = cmd.gate
    if g == QFT or get_inverse(g) == QFT or g == Swap:
        return True
    if isinstance(g, BasicMathGate):
        return False
    return eng.next_engine.is_available(cmd)

def get_main_engine(sim):
    engine_list = [
        AutoReplacer(rule_set),
        InstructionFilter(high_level_gates),
        TagRemover(),
        LocalOptimizer(3),
        AutoReplacer(rule_set),
        TagRemover(),
        LocalOptimizer(3),
    ]
    return MainEngine(sim, engine_list)

def test_factoring(sim):
    eng = get_main_engine(sim)

    ctrl_qubit = eng.allocate_qubit()

    N = 15
    a = 2

    x = eng.allocate_qureg(4)
    X | x[0]

    H | ctrl_qubit
    with Control(eng, ctrl_qubit):
        MultiplyByConstantModN(pow(a, 2**7, N), N) | x

    H | ctrl_qubit
    eng.flush()
    cheat_tpl = sim.cheat()
    idx = cheat_tpl[0][ctrl_qubit[0].id]
    vec = cheat_tpl[1]

    for i in range(len(vec)):
        if abs(vec[i]) > 1.0e-8:
            assert ((i >> idx) & 1) == 0

    Measure | ctrl_qubit
    assert int(ctrl_qubit) == 0
    del vec, cheat_tpl

    H | ctrl_qubit
    with Control(eng, ctrl_qubit):
        MultiplyByConstantModN(pow(a, 2, N), N) | x

    H | ctrl_qubit
    eng.flush()
    cheat_tpl = sim.cheat()
    idx = cheat_tpl[0][ctrl_qubit[0].id]
    vec = cheat_tpl[1]

    probability = 0.0
    for i in range(len(vec)):
        if abs(vec[i]) > 1.0e-8:
            if ((i >> idx) & 1) == 0:
                probability += abs(vec[i]) ** 2

    assert probability == pytest.approx(0.5)

    Measure | ctrl_qubit
    All(Measure) | x