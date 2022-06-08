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
Register a decomposition rule for multi-controlled gates.

Implements the decomposition of Nielsen and Chuang (Fig. 4.10) which
decomposes a C^n(U) gate into a sequence of 2 * (n-1) Toffoli gates and one
C(U) gate by using (n-1) ancilla qubits and circuit depth of 2n-1.
"""

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute, get_control_count
from divya.ops import BasicGate, Toffoli, XGate

def _recognize_CnU(cmd):  # pylint: disable=invalid-name
    """Recognize an arbitrary gate which has n>=2 control qubits, except a Toffoli gate."""
    if get_control_count(cmd) == 2:
        if not isinstance(cmd.gate, XGate):
            return True
    elif get_control_count(cmd) > 2:
        return True
    return False

def _decompose_CnU(cmd):  # pylint: disable=invalid-name
    """
    Decompose a multi-controlled gate U with n control qubits into a single- controlled U.

    It uses (n-1) work qubits and 2 * (n-1) Toffoli gates for general U and (n-2) work qubits and 2n - 3 Toffoli gates
    if U is an X-gate.
    """
    eng = cmd.engine
    qubits = cmd.qubits
    ctrl_qureg = cmd.control_qubits
    gate = cmd.gate
    n_controls = get_control_count(cmd)

    # specialized for X-gate
    if gate == XGate() and n_controls > 2:
        n_controls -= 1
    ancilla_qureg = eng.allocate_qureg(n_controls - 1)

    with Compute(eng):
        Toffoli | (ctrl_qureg[0], ctrl_qureg[1], ancilla_qureg[0])
        for ctrl_index in range(2, n_controls):
            Toffoli | (
                ctrl_qureg[ctrl_index],
                ancilla_qureg[ctrl_index - 2],
                ancilla_qureg[ctrl_index - 1],
            )
    ctrls = [ancilla_qureg[-1]]

    # specialized for X-gate
    if gate == XGate() and get_control_count(cmd) > 2:
        ctrls += [ctrl_qureg[-1]]
    with Control(eng, ctrls):
        gate | qubits

    Uncompute(eng)

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(BasicGate, _decompose_CnU, _recognize_CnU)]