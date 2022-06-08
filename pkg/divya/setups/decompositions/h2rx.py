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

"""Register a decomposition for the H gate into an Ry and Rx gate."""

import math

from divya.cengines import DecompositionRule
from divya.meta import get_control_count
from divya.ops import H, Ph, Rx, Ry

def _decompose_h2rx_M(cmd):  # pylint: disable=invalid-name
    """Decompose the Ry gate."""
    # Labelled 'M' for 'minus' because decomposition ends with a Ry(-pi/2)
    qubit = cmd.qubits[0]
    Rx(math.pi) | qubit
    Ph(math.pi / 2) | qubit
    Ry(-1 * math.pi / 2) | qubit

def _decompose_h2rx_N(cmd):  # pylint: disable=invalid-name
    """Decompose the Ry gate."""
    # Labelled 'N' for 'neutral' because decomposition doesn't end with
    # Ry(pi/2) or Ry(-pi/2)
    qubit = cmd.qubits[0]
    Ry(math.pi / 2) | qubit
    Ph(3 * math.pi / 2) | qubit
    Rx(-1 * math.pi) | qubit

def _recognize_HNoCtrl(cmd):  # pylint: disable=invalid-name
    """For efficiency reasons only if no control qubits."""
    return get_control_count(cmd) == 0

#: Decomposition rules
all_defined_decomposition_rules = [
    DecompositionRule(H.__class__, _decompose_h2rx_N, _recognize_HNoCtrl),
    DecompositionRule(H.__class__, _decompose_h2rx_M, _recognize_HNoCtrl),
]