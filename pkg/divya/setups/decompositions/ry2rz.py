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

"""Register a decomposition for the Ry gate into an Rz and Rx(pi/2) gate."""

import math

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute, get_control_count
from divya.ops import Rx, Ry, Rz

def _decompose_ry(cmd):
    """Decompose the Ry gate."""
    qubit = cmd.qubits[0]
    eng = cmd.engine
    angle = cmd.gate.angle

    with Control(eng, cmd.control_qubits):
        with Compute(eng):
            Rx(math.pi / 2.0) | qubit
        Rz(angle) | qubit
        Uncompute(eng)

def _recognize_RyNoCtrl(cmd):  # pylint: disable=invalid-name
    """For efficiency reasons only if no control qubits."""
    return get_control_count(cmd) == 0

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(Ry, _decompose_ry, _recognize_RyNoCtrl)]