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
from divya.cengines import MainEngine
from divya.backends import Simulator
from divya.cengines import AutoReplacer, DecompositionRuleSet, InstructionFilter
from divya.libs.math import (
    AddQuantum,
    ComparatorQuantum,
    DivideQuantum,
    MultiplyQuantum,
    SubtractQuantum,
)
from divya.meta import Compute, Control, Dagger, Uncompute
from divya.ops import All, BasicMathGate, ClassicalInstructionGate, Measure, X
from divya.setups.decompositions import swap2cnot

def print_all_probabilities(eng, qureg):
    i = 0
    y = len(qureg)
    while i < (2**y):
        qubit_list = [int(x) for x in list(('{0:0b}'.format(i)).zfill(y))]
        qubit_list = qubit_list[::-1]
        prob = eng.backend.get_probability(qubit_list, qureg)
        if prob != 0.0:
            print(prob, qubit_list, i)
        i += 1

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

rule_set = DecompositionRuleSet(modules=[divya.libs.math, swap2cnot])

@pytest.fixture
def eng():
    return MainEngine(
        backend=Simulator(),
        engine_list=[AutoReplacer(rule_set), InstructionFilter(no_math_emulation)],
    )

@pytest.mark.parametrize('carry', (False, True))
@pytest.mark.parametrize('inverse', (False, True))
@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantumadder_size_mismatch(eng, qubit_idx, inverse, carry):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    qureg_c = eng.allocate_qureg(1 if qubit_idx != 2 else 2)

    if carry and inverse:
        pytest.skip('Inverse addition with carry not supported')
    elif not carry and qubit_idx == 2:
        pytest.skip('Invalid test parameter combination')

    with pytest.raises(ValueError):
        if inverse:
            with Dagger(eng):
                AddQuantum | (qureg_a, qureg_b, qureg_c if carry else [])
        else:
            AddQuantum | (qureg_a, qureg_b, qureg_c if carry else [])

@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantum_conditional_adder_size_mismatch(eng, qubit_idx):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    control = eng.allocate_qureg(1 if qubit_idx != 2 else 2)

    with pytest.raises(ValueError):
        with Control(eng, control):
            AddQuantum | (qureg_a, qureg_b)

@pytest.mark.parametrize('inverse', (False, True))
@pytest.mark.parametrize('qubit_idx', (0, 1, 2, 3))
def test_quantum_conditional_add_carry_size_mismatch(eng, qubit_idx, inverse):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    qureg_c = eng.allocate_qureg(2 if qubit_idx != 2 else 3)
    control = eng.allocate_qureg(1 if qubit_idx != 3 else 2)

    with pytest.raises(ValueError):
        with Control(eng, control):
            if inverse:
                with Dagger(eng):
                    AddQuantum | (qureg_a, qureg_b, qureg_c)
            else:
                AddQuantum | (qureg_a, qureg_b, qureg_c)

def test_quantum_adder(eng):
    qureg_a = eng.allocate_qureg(4)
    qureg_b = eng.allocate_qureg(4)
    control_qubit = eng.allocate_qubit()

    init(eng, qureg_a, 2)
    init(eng, qureg_b, 1)
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 0, 0], qureg_b))

    with Control(eng, control_qubit):
        AddQuantum | (qureg_a, qureg_b)

    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 0, 0], qureg_b))

    X | control_qubit

    with Control(eng, control_qubit):
        AddQuantum | (qureg_a, qureg_b)

    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 0], qureg_b))

    init(eng, qureg_a, 2)  # reset
    init(eng, qureg_b, 3)  # reset

    c = eng.allocate_qubit()
    init(eng, qureg_a, 15)
    init(eng, qureg_b, 15)

    AddQuantum | (qureg_a, qureg_b, c)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 1, 1], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1], c))

    with Compute(eng):
        with Control(eng, control_qubit):
            AddQuantum | (qureg_a, qureg_b)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 1, 1], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1], c))

    AddQuantum | (qureg_a, qureg_b)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 1], qureg_b))

    with Compute(eng):
        AddQuantum | (qureg_a, qureg_b)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 1], qureg_b))

    d = eng.allocate_qureg(2)

    with Compute(eng):
        with Control(eng, control_qubit):
            AddQuantum | (qureg_a, qureg_b, d)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 1], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 0], d))

    All(Measure) | qureg_b
    Measure | c

def test_quantumsubtraction(eng):
    qureg_a = eng.allocate_qureg(4)
    qureg_b = eng.allocate_qureg(4)
    control_qubit = eng.allocate_qubit()

    init(eng, qureg_a, 5)
    init(eng, qureg_b, 7)

    X | control_qubit
    with Control(eng, control_qubit):
        SubtractQuantum | (qureg_a, qureg_b)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 0, 0, 0], qureg_b))

    # Size mismatch
    with pytest.raises(ValueError):
        SubtractQuantum | (qureg_a, qureg_b[:-1])
        eng.flush()

    init(eng, qureg_a, 5)  # reset
    init(eng, qureg_b, 2)  # reset

    init(eng, qureg_a, 5)
    init(eng, qureg_b, 3)

    SubtractQuantum | (qureg_a, qureg_b)

    print_all_probabilities(eng, qureg_b)
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 1, 1, 0], qureg_b))

    init(eng, qureg_a, 5)  # reset
    init(eng, qureg_b, 14)  # reset
    init(eng, qureg_a, 5)
    init(eng, qureg_b, 3)

    with Compute(eng):
        SubtractQuantum | (qureg_a, qureg_b)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 0, 0], qureg_b))
    All(Measure) | qureg_a
    All(Measure) | qureg_b

def test_comparator(eng):
    qureg_a = eng.allocate_qureg(3)
    qureg_b = eng.allocate_qureg(3)
    compare_qubit = eng.allocate_qubit()

    init(eng, qureg_a, 5)
    init(eng, qureg_b, 3)

    ComparatorQuantum | (qureg_a, qureg_b, compare_qubit)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1], compare_qubit))

    # Size mismatch in qubit registers
    with pytest.raises(ValueError):
        ComparatorQuantum | (qureg_a, qureg_b[:-1], compare_qubit)

    # Only single qubit for compare qubit
    with pytest.raises(ValueError):
        ComparatorQuantum | (qureg_a, qureg_b, [*compare_qubit, *compare_qubit])

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    Measure | compare_qubit

@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantumdivision_size_mismatch(eng, qubit_idx):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    qureg_c = eng.allocate_qureg(4 if qubit_idx != 2 else 3)

    with pytest.raises(ValueError):
        DivideQuantum | (qureg_a, qureg_b, qureg_c)

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantumdivision_size_mismatch_inverse(eng, qubit_idx):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    qureg_c = eng.allocate_qureg(4 if qubit_idx != 2 else 3)

    with pytest.raises(ValueError):
        with Dagger(eng):
            DivideQuantum | (qureg_a, qureg_b, qureg_c)

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

def test_quantumdivision(eng):
    qureg_a = eng.allocate_qureg(4)
    qureg_b = eng.allocate_qureg(4)
    qureg_c = eng.allocate_qureg(4)

    init(eng, qureg_a, 10)
    init(eng, qureg_c, 3)

    DivideQuantum | (qureg_a, qureg_b, qureg_c)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 0, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 0], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 0], qureg_c))

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

    init(eng, qureg_a, 1)  # reset
    init(eng, qureg_b, 3)  # reset

    init(eng, qureg_a, 11)

    with Compute(eng):
        DivideQuantum | (qureg_a, qureg_b, qureg_c)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 0, 0, 0], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0, 0], qureg_c))

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantummultiplication_size_mismatch(eng, qubit_idx):
    qureg_a = eng.allocate_qureg(3 if qubit_idx != 0 else 2)
    qureg_b = eng.allocate_qureg(3 if qubit_idx != 1 else 2)
    qureg_c = eng.allocate_qureg(7 if qubit_idx != 2 else 6)

    with pytest.raises(ValueError):
        MultiplyQuantum | (qureg_a, qureg_b, qureg_c)

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

@pytest.mark.parametrize('qubit_idx', (0, 1, 2))
def test_quantummultiplication_size_mismatch_inverse(eng, qubit_idx):
    qureg_a = eng.allocate_qureg(4 if qubit_idx != 0 else 3)
    qureg_b = eng.allocate_qureg(4 if qubit_idx != 1 else 3)
    qureg_c = eng.allocate_qureg(4 if qubit_idx != 2 else 3)

    with pytest.raises(ValueError):
        with Dagger(eng):
            MultiplyQuantum | (qureg_a, qureg_b, qureg_c)

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

def test_quantummultiplication(eng):
    qureg_a = eng.allocate_qureg(3)
    qureg_b = eng.allocate_qureg(3)
    qureg_c = eng.allocate_qureg(7)

    init(eng, qureg_a, 7)
    init(eng, qureg_b, 3)

    MultiplyQuantum | (qureg_a, qureg_b, qureg_c)

    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 1], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 0, 1, 0, 1, 0, 0], qureg_c))

    All(Measure) | qureg_a
    All(Measure) | qureg_b
    All(Measure) | qureg_c

    init(eng, qureg_a, 7)
    init(eng, qureg_b, 3)
    init(eng, qureg_c, 21)

    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 0, 0, 0, 0, 0, 0], qureg_c))
    init(eng, qureg_a, 2)
    init(eng, qureg_b, 3)

    with Compute(eng):
        MultiplyQuantum | (qureg_a, qureg_b, qureg_c)
    Uncompute(eng)

    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 1, 0], qureg_a))
    assert 1.0 == pytest.approx(eng.backend.get_probability([1, 1, 0], qureg_b))
    assert 1.0 == pytest.approx(eng.backend.get_probability([0, 0, 0, 0, 0, 0, 0], qureg_c))