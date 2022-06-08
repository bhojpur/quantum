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
Registers a decomposition for the controlled global phase gate.

Turns the controlled global phase gate into a (controlled) phase-shift gate.
Each time this rule is applied, one control can be shaved off.
"""

from divya.cengines import DecompositionRule
from divya.meta import Control, get_control_count
from divya.ops import Ph, R

def _decompose_Ph(cmd):  # pylint: disable=invalid-name
    """Decompose the controlled phase gate (C^nPh(phase))."""
    ctrl = cmd.control_qubits
    gate = cmd.gate
    eng = cmd.engine

    with Control(eng, ctrl[1:]):
        R(gate.angle) | ctrl[0]

def _recognize_Ph(cmd):  # pylint: disable=invalid-name
    """Recognize the controlled phase gate."""
    return get_control_count(cmd) >= 1

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(Ph, _decompose_Ph, _recognize_Ph)]