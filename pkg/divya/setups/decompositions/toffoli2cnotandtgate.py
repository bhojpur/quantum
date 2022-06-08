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
Registers a decomposition rule for the Toffoli gate.

Decomposes the Toffoli gate using Hadamard, T, Tdag, and CNOT gates.
"""

from divya.cengines import DecompositionRule
from divya.meta import get_control_count
from divya.ops import CNOT, NOT, H, T, Tdag

def _decompose_toffoli(cmd):
    """Decompose the Toffoli gate into CNOT, H, T, and Tdagger gates."""
    ctrl = cmd.control_qubits

    target = cmd.qubits[0]

    H | target
    CNOT | (ctrl[0], target)
    T | ctrl[0]
    Tdag | target
    CNOT | (ctrl[1], target)
    CNOT | (ctrl[1], ctrl[0])
    Tdag | ctrl[0]
    T | target
    CNOT | (ctrl[1], ctrl[0])
    CNOT | (ctrl[0], target)
    Tdag | target
    CNOT | (ctrl[1], target)
    T | target
    T | ctrl[1]
    H | target

def _recognize_toffoli(cmd):
    """Recognize the Toffoli gate."""
    return get_control_count(cmd) == 2

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(NOT.__class__, _decompose_toffoli, _recognize_toffoli)]