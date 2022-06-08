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
Register a decomposition to replace turn negatively controlled qubits into positively controlled qubits.

This achived by applying X gates to selected qubits.
"""

from copy import deepcopy

from divya.cengines import DecompositionRule
from divya.meta import Compute, Uncompute, has_negative_control
from divya.ops import BasicGate, X

def _decompose_controlstate(cmd):
    """Decompose commands with control qubits in negative state (ie. control qubits with state '0' instead of '1')."""
    with Compute(cmd.engine):
        for state, ctrl in zip(cmd.control_state, cmd.control_qubits):
            if state == '0':
                X | ctrl

    # Resend the command with the `control_state` cleared
    cmd.ctrl_state = '1' * len(cmd.control_state)
    orig_engine = cmd.engine
    cmd.engine.receive([deepcopy(cmd)])  # NB: deepcopy required here to workaround infinite recursion detection
    Uncompute(orig_engine)

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(BasicGate, _decompose_controlstate, has_negative_control)]