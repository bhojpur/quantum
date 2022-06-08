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
Registers a decomposition rule for the quantum Fourier transform.

Decomposes the QFT gate into Hadamard and controlled phase-shift gates (R).

Warning:
    The final Swaps are not included, as those are simply a re-indexing of
    quantum registers.
"""

import math

from divya.cengines import DecompositionRule
from divya.meta import Control
from divya.ops import QFT, H, R

def _decompose_QFT(cmd):  # pylint: disable=invalid-name
    qb = cmd.qubits[0]
    eng = cmd.engine
    with Control(eng, cmd.control_qubits):
        for i in range(len(qb)):
            H | qb[-1 - i]
            for j in range(len(qb) - 1 - i):
                with Control(eng, qb[-1 - (j + i + 1)]):
                    R(math.pi / (1 << (1 + j))) | qb[-1 - i]

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(QFT.__class__, _decompose_QFT)]