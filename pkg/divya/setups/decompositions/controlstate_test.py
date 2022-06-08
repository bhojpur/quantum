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
Tests for the controlstate decomposition rule.
"""

from divya import MainEngine
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
)
from divya.meta import Control, has_negative_control
from divya.ops import X
from divya.setups.decompositions import cnot2cz, controlstate

def filter_func(eng, cmd):
    if has_negative_control(cmd):
        return False
    return True

def test_controlstate_priority():
    saving_backend = DummyEngine(save_commands=True)
    rule_set = DecompositionRuleSet(modules=[cnot2cz, controlstate])
    eng = MainEngine(backend=saving_backend, engine_list=[AutoReplacer(rule_set), InstructionFilter(filter_func)])
    qubit1 = eng.allocate_qubit()
    qubit2 = eng.allocate_qubit()
    qubit3 = eng.allocate_qubit()
    with Control(eng, qubit2, ctrl_state='0'):
        X | qubit1
    with Control(eng, qubit3, ctrl_state='1'):
        X | qubit1
    eng.flush()

    assert len(saving_backend.received_commands) == 8
    for cmd in saving_backend.received_commands:
        assert not has_negative_control(cmd)