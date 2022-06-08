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

"Tests for divya.setups.decompositions.ry2rz.py"

import math

import pytest

from divya.backends import Simulator
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    DummyEngine,
    InstructionFilter,
    MainEngine,
)
from divya.meta import Control
from divya.ops import Measure, Ry

from . import ry2rz

def test_recognize_correct_gates():
    saving_backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=saving_backend)
    qubit = eng.allocate_qubit()
    ctrl_qubit = eng.allocate_qubit()
    eng.flush()
    Ry(0.3) | qubit
    with Control(eng, ctrl_qubit):
        Ry(0.4) | qubit
    eng.flush(deallocate_qubits=True)
    assert ry2rz._recognize_RyNoCtrl(saving_backend.received_commands[3])
    assert not ry2rz._recognize_RyNoCtrl(saving_backend.received_commands[4])

def ry_decomp_gates(eng, cmd):
    g = cmd.gate
    if isinstance(g, Ry):
        return False
    else:
        return True

@pytest.mark.parametrize("angle", [0, math.pi, 2 * math.pi, 4 * math.pi, 0.5])
def test_decomposition(angle):
    for basis_state in ([1, 0], [0, 1]):
        correct_dummy_eng = DummyEngine(save_commands=True)
        correct_eng = MainEngine(backend=Simulator(), engine_list=[correct_dummy_eng])

        rule_set = DecompositionRuleSet(modules=[ry2rz])
        test_dummy_eng = DummyEngine(save_commands=True)
        test_eng = MainEngine(
            backend=Simulator(),
            engine_list=[
                AutoReplacer(rule_set),
                InstructionFilter(ry_decomp_gates),
                test_dummy_eng,
            ],
        )

        correct_qb = correct_eng.allocate_qubit()
        Ry(angle) | correct_qb
        correct_eng.flush()

        test_qb = test_eng.allocate_qubit()
        Ry(angle) | test_qb
        test_eng.flush()

        assert correct_dummy_eng.received_commands[1].gate == Ry(angle)
        assert test_dummy_eng.received_commands[1].gate != Ry(angle)

        for fstate in ['0', '1']:
            test = test_eng.backend.get_amplitude(fstate, test_qb)
            correct = correct_eng.backend.get_amplitude(fstate, correct_qb)
            assert correct == pytest.approx(test, rel=1e-12, abs=1e-12)

        Measure | test_qb
        Measure | correct_qb