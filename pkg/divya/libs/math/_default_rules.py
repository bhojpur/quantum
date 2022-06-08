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

"""Registers a few default replacement rules for Shor's algorithm to work."""

from divya.cengines import DecompositionRule
from divya.meta import Control

from ._constantmath import add_constant, add_constant_modN, mul_by_constant_modN
from ._gates import (
    AddConstant,
    AddConstantModN,
    AddQuantum,
    ComparatorQuantum,
    DivideQuantum,
    MultiplyByConstantModN,
    MultiplyQuantum,
    SubtractQuantum,
    _InverseAddQuantumGate,
    _InverseDivideQuantumGate,
    _InverseMultiplyQuantumGate,
)
from ._quantummath import (
    add_quantum,
    comparator,
    inverse_add_quantum_carry,
    inverse_quantum_division,
    inverse_quantum_multiplication,
    quantum_conditional_add,
    quantum_conditional_add_carry,
    quantum_division,
    quantum_multiplication,
    subtract_quantum,
)

def _replace_addconstant(cmd):
    eng = cmd.engine
    const = cmd.gate.a
    quint = cmd.qubits[0]

    with Control(eng, cmd.control_qubits):
        add_constant(eng, const, quint)

def _replace_addconstmodN(cmd):  # pylint: disable=invalid-name
    eng = cmd.engine
    const = cmd.gate.a
    N = cmd.gate.N
    quint = cmd.qubits[0]

    with Control(eng, cmd.control_qubits):
        add_constant_modN(eng, const, N, quint)

def _replace_multiplybyconstantmodN(cmd):  # pylint: disable=invalid-name
    eng = cmd.engine
    const = cmd.gate.a
    N = cmd.gate.N
    quint = cmd.qubits[0]

    with Control(eng, cmd.control_qubits):
        mul_by_constant_modN(eng, const, N, quint)

def _replace_addquantum(cmd):
    eng = cmd.engine
    if cmd.control_qubits == []:
        quint_a = cmd.qubits[0]
        quint_b = cmd.qubits[1]
        if len(cmd.qubits) == 3:
            carry = cmd.qubits[2]
            add_quantum(eng, quint_a, quint_b, carry)
        else:
            add_quantum(eng, quint_a, quint_b)
    else:
        quint_a = cmd.qubits[0]
        quint_b = cmd.qubits[1]
        if len(cmd.qubits) == 3:
            carry = cmd.qubits[2]
            with Control(eng, cmd.control_qubits):
                quantum_conditional_add_carry(eng, quint_a, quint_b, cmd.control_qubits, carry)
        else:
            with Control(eng, cmd.control_qubits):
                quantum_conditional_add(eng, quint_a, quint_b, cmd.control_qubits)

def _replace_inverse_add_quantum(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]

    if len(cmd.qubits) == 3:
        quint_c = cmd.qubits[2]
        with Control(eng, cmd.control_qubits):
            inverse_add_quantum_carry(eng, quint_a, [quint_b, quint_c])
    else:
        with Control(eng, cmd.control_qubits):
            subtract_quantum(eng, quint_a, quint_b)

def _replace_comparator(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]
    carry = cmd.qubits[2]

    with Control(eng, cmd.control_qubits):
        comparator(eng, quint_a, quint_b, carry)

def _replace_quantumdivision(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]
    quint_c = cmd.qubits[2]

    with Control(eng, cmd.control_qubits):
        quantum_division(eng, quint_a, quint_b, quint_c)

def _replace_inversequantumdivision(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]
    quint_c = cmd.qubits[2]

    with Control(eng, cmd.control_qubits):
        inverse_quantum_division(eng, quint_a, quint_b, quint_c)

def _replace_quantummultiplication(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]
    quint_c = cmd.qubits[2]

    with Control(eng, cmd.control_qubits):
        quantum_multiplication(eng, quint_a, quint_b, quint_c)

def _replace_inversequantummultiplication(cmd):
    eng = cmd.engine
    quint_a = cmd.qubits[0]
    quint_b = cmd.qubits[1]
    quint_c = cmd.qubits[2]

    with Control(eng, cmd.control_qubits):
        inverse_quantum_multiplication(eng, quint_a, quint_b, quint_c)

all_defined_decomposition_rules = [
    DecompositionRule(AddConstant, _replace_addconstant),
    DecompositionRule(AddConstantModN, _replace_addconstmodN),
    DecompositionRule(MultiplyByConstantModN, _replace_multiplybyconstantmodN),
    DecompositionRule(AddQuantum.__class__, _replace_addquantum),
    DecompositionRule(_InverseAddQuantumGate, _replace_inverse_add_quantum),
    DecompositionRule(SubtractQuantum.__class__, _replace_inverse_add_quantum),
    DecompositionRule(ComparatorQuantum.__class__, _replace_comparator),
    DecompositionRule(DivideQuantum.__class__, _replace_quantumdivision),
    DecompositionRule(_InverseDivideQuantumGate, _replace_inversequantumdivision),
    DecompositionRule(MultiplyQuantum.__class__, _replace_quantummultiplication),
    DecompositionRule(_InverseMultiplyQuantumGate, _replace_inversequantummultiplication),
]