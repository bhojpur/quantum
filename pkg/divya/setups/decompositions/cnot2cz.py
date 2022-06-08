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

"""Registers a decomposition to for a CNOT gate in terms of CZ and Hadamard."""

from divya.cengines import DecompositionRule
from divya.meta import Compute, Uncompute, get_control_count
from divya.ops import CZ, H, X

def _decompose_cnot(cmd):
    """Decompose CNOT gates."""
    ctrl = cmd.control_qubits
    eng = cmd.engine
    with Compute(eng):
        H | cmd.qubits[0]
    CZ | (ctrl[0], cmd.qubits[0][0])
    Uncompute(eng)

def _recognize_cnot(cmd):
    return get_control_count(cmd) == 1

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(X.__class__, _decompose_cnot, _recognize_cnot)]