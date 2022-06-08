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
Registers a decomposition to achieve a Swap gate.

Decomposes a Swap gate using 3 CNOT gates, where the one in the middle
features as many control qubits as the Swap gate has control qubits.
"""

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute
from divya.ops import CNOT, Swap

def _decompose_swap(cmd):
    """Decompose (controlled) swap gates."""
    ctrl = cmd.control_qubits
    eng = cmd.engine
    with Compute(eng):
        CNOT | (cmd.qubits[0], cmd.qubits[1])
    with Control(eng, ctrl):
        CNOT | (cmd.qubits[1], cmd.qubits[0])
    Uncompute(eng)

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(Swap.__class__, _decompose_swap)]