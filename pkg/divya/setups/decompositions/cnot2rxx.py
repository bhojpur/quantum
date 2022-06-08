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

"""Register a decomposition to for a CNOT gate in terms of Rxx, Rx and Ry gates."""

import math

from divya.cengines import DecompositionRule
from divya.meta import get_control_count
from divya.ops import Ph, Rx, Rxx, Ry, X

def _decompose_cnot2rxx_M(cmd):  # pylint: disable=invalid-name
    """Decompose CNOT gate into Rxx gate."""
    # Labelled 'M' for 'minus' because decomposition ends with a Ry(-pi/2)
    ctrl = cmd.control_qubits
    Ry(math.pi / 2) | ctrl[0]
    Ph(7 * math.pi / 4) | ctrl[0]
    Rx(-math.pi / 2) | ctrl[0]
    Rx(-math.pi / 2) | cmd.qubits[0][0]
    Rxx(math.pi / 2) | (ctrl[0], cmd.qubits[0][0])
    Ry(-1 * math.pi / 2) | ctrl[0]

def _decompose_cnot2rxx_P(cmd):  # pylint: disable=invalid-name
    """Decompose CNOT gate into Rxx gate."""
    # Labelled 'P' for 'plus' because decomposition ends with a Ry(+pi/2)
    ctrl = cmd.control_qubits
    Ry(-math.pi / 2) | ctrl[0]
    Ph(math.pi / 4) | ctrl[0]
    Rx(-math.pi / 2) | ctrl[0]
    Rx(math.pi / 2) | cmd.qubits[0][0]
    Rxx(math.pi / 2) | (ctrl[0], cmd.qubits[0][0])
    Ry(math.pi / 2) | ctrl[0]

def _recognize_cnot2(cmd):
    """Identify that the command is a CNOT gate (control - X gate)."""
    return get_control_count(cmd) == 1

#: Decomposition rules
all_defined_decomposition_rules = [
    DecompositionRule(X.__class__, _decompose_cnot2rxx_M, _recognize_cnot2),
    DecompositionRule(X.__class__, _decompose_cnot2rxx_P, _recognize_cnot2),
]