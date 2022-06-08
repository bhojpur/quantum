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

"""Tests for divya.libs.math_constantmath.py."""

import pytest

import divya.libs.math
from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import AutoReplacer, DecompositionRuleSet, InstructionFilter
from divya.libs.math import AddConstant, AddConstantModN, MultiplyByConstantModN
from divya.ops import All, BasicMathGate, ClassicalInstructionGate, Measure, X
from divya.setups.decompositions import qft2crandhadamard, swap2cnot

def init(engine, quint, value):
    for i in range(len(quint)):
        if ((value >> i) & 1) == 1:
            X | quint[i]

def no_math_emulation(eng, cmd):
    if isinstance(cmd.gate, BasicMathGate):
        return False
    if isinstance(cmd.gate, ClassicalInstructionGate):
        return True
    try:
        return len(cmd.gate.matrix) == 2
    except AttributeError:
        return False

@pytest.fixture
def eng():
    return MainEngine(
        backend=Simulator(),
        engine_list=[AutoReplacer(rule_set), InstructionFilter(no_math_emulation)],
    )

rule_set = DecompositionRuleSet(modules=[divya.libs.math, qft2crandhadamard, swap2cnot])

@pytest.mark.parametrize(
    'gate', (AddConstantModN(-1, 6), MultiplyByConstantModN(-1, 6), MultiplyByConstantModN(4, 4)), ids=str
)
def test_invalid(eng, gate):
    qureg = eng.allocate_qureg(4)
    init(eng, qureg, 4)

    with pytest.raises(ValueError):
        gate | qureg
        eng.flush()

def test_adder(eng):
    qureg = eng.allocate_qureg(4)
    init(eng, qureg, 4)

    AddConstant(3) | qureg

    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][7]))

    init(eng, qureg, 7)  # reset
    init(eng, qureg, 2)

    # check for overflow -> should be 15+2 = 1 (mod 16)
    AddConstant(15) | qureg
    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][1]))

    All(Measure) | qureg

def test_modadder(eng):
    qureg = eng.allocate_qureg(4)
    init(eng, qureg, 4)

    AddConstantModN(3, 6) | qureg

    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][1]))

    init(eng, qureg, 1)  # reset
    init(eng, qureg, 7)

    AddConstantModN(10, 13) | qureg
    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][4]))

    All(Measure) | qureg

def test_modmultiplier(eng):
    qureg = eng.allocate_qureg(4)
    init(eng, qureg, 4)

    MultiplyByConstantModN(3, 7) | qureg

    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][5]))

    init(eng, qureg, 5)  # reset
    init(eng, qureg, 7)

    MultiplyByConstantModN(4, 13) | qureg
    assert 1.0 == pytest.approx(abs(eng.backend.cheat()[1][2]))

    All(Measure) | qureg