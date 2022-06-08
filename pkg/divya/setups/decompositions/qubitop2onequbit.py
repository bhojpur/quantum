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

"""Register a decomposition rule for a unitary QubitOperator to one qubit gates."""

import cmath

from divya.cengines import DecompositionRule
from divya.meta import Control, get_control_count
from divya.ops import Ph, QubitOperator, X, Y, Z

def _recognize_qubitop(cmd):
    """For efficiency only use this if at most 1 control qubit."""
    return get_control_count(cmd) <= 1

def _decompose_qubitop(cmd):
    if len(cmd.qubits) != 1:
        raise ValueError('QubitOperator decomposition can only accept a single quantum register')
    qureg = cmd.qubits[0]
    eng = cmd.engine
    qubit_op = cmd.gate
    with Control(eng, cmd.control_qubits):
        ((term, coefficient),) = qubit_op.terms.items()
        phase = cmath.phase(coefficient)
        Ph(phase) | qureg[0]
        for index, action in term:
            if action == "X":
                X | qureg[index]
            elif action == "Y":
                Y | qureg[index]
            elif action == "Z":
                Z | qureg[index]

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(QubitOperator, _decompose_qubitop, _recognize_qubitop)]