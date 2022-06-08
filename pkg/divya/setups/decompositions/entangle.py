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
Registers a decomposition for the Entangle gate.

Applies a Hadamard gate to the first qubit and then, conditioned on this first
qubit, CNOT gates to all others.
"""

from divya.cengines import DecompositionRule
from divya.meta import Control
from divya.ops import All, Entangle, H, X

def _decompose_entangle(cmd):
    """Decompose the entangle gate."""
    qureg = cmd.qubits[0]
    eng = cmd.engine

    with Control(eng, cmd.control_qubits):
        H | qureg[0]
        with Control(eng, qureg[0]):
            All(X) | qureg[1:]

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(Entangle.__class__, _decompose_entangle)]