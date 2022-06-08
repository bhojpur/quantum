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

"""Registers a decomposition for the Rz gate into an Rx and Ry(pi/2) or Ry(-pi/2) gate."""

import math

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute, get_control_count
from divya.ops import Rx, Ry, Rz

def _decompose_rz2rx_P(cmd):  # pylint: disable=invalid-name
    """Decompose the Rz using negative angle."""
    # Labelled 'P' for 'plus' because decomposition ends with a Ry(+pi/2)
    qubit = cmd.qubits[0]
    eng = cmd.engine
    angle = cmd.gate.angle

    with Control(eng, cmd.control_qubits):
        with Compute(eng):
            Ry(-math.pi / 2.0) | qubit
        Rx(-angle) | qubit
        Uncompute(eng)

def _decompose_rz2rx_M(cmd):  # pylint: disable=invalid-name
    """Decompose the Rz using positive angle."""
    # Labelled 'M' for 'minus' because decomposition ends with a Ry(-pi/2)
    qubit = cmd.qubits[0]
    eng = cmd.engine
    angle = cmd.gate.angle

    with Control(eng, cmd.control_qubits):
        with Compute(eng):
            Ry(math.pi / 2.0) | qubit
        Rx(angle) | qubit
        Uncompute(eng)

def _recognize_RzNoCtrl(cmd):  # pylint: disable=invalid-name
    """Decompose the gate only if the command represents a single qubit gate (if it is not part of a control gate)."""
    return get_control_count(cmd) == 0

#: Decomposition rules
all_defined_decomposition_rules = [
    DecompositionRule(Rz, _decompose_rz2rx_P, _recognize_RzNoCtrl),
    DecompositionRule(Rz, _decompose_rz2rx_M, _recognize_RzNoCtrl),
]