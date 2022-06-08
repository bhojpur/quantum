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

"""Register a decomposition to achieve a SqrtSwap gate."""

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute
from divya.ops import CNOT, SqrtSwap, SqrtX

def _decompose_sqrtswap(cmd):
    """Decompose (controlled) swap gates."""
    if len(cmd.qubits) != 2:
        raise ValueError('SqrtSwap gate requires two quantum registers')
    if not (len(cmd.qubits[0]) == 1 and len(cmd.qubits[1]) == 1):
        raise ValueError('SqrtSwap gate requires must act on only 2 qubits')
    ctrl = cmd.control_qubits
    qubit0 = cmd.qubits[0][0]
    qubit1 = cmd.qubits[1][0]
    eng = cmd.engine

    with Control(eng, ctrl):
        with Compute(eng):
            CNOT | (qubit0, qubit1)
        with Control(eng, qubit1):
            SqrtX | qubit0
        Uncompute(eng)

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(SqrtSwap.__class__, _decompose_sqrtswap)]