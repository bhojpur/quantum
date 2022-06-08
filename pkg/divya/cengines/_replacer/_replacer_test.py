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

"""Tests for divya.cengines._replacer._replacer.py."""

import pytest

from divya import MainEngine
from divya.cengines import DecompositionRule, DecompositionRuleSet, DummyEngine
from divya.cengines._replacer import _replacer
from divya.ops import (
    BasicGate,
    ClassicalInstructionGate,
    Command,
    H,
    NotInvertible,
    Rx,
    S,
    X,
)

def test_filter_engine():
    def my_filter(self, cmd):
        if cmd.gate == H:
            return True
        return False

    filter_eng = _replacer.InstructionFilter(my_filter)
    eng = MainEngine(backend=DummyEngine(), engine_list=[filter_eng])
    qubit = eng.allocate_qubit()
    cmd = Command(eng, H, (qubit,))
    cmd2 = Command(eng, X, (qubit,))
    assert eng.is_available(cmd)
    assert not eng.is_available(cmd2)
    assert filter_eng.is_available(cmd)
    assert not filter_eng.is_available(cmd2)

class SomeGateClass(BasicGate):
    """Test gate class"""

    pass

SomeGate = SomeGateClass()

def make_decomposition_rule_set():
    result = DecompositionRuleSet()
    # BasicGate with no get_inverse used for testing:
    with pytest.raises(NotInvertible):
        SomeGate.get_inverse()

    # Loading of decomposition rules:
    def decompose_test1(cmd):
        qb = cmd.qubits
        X | qb

    def recognize_test(cmd):
        return True

    result.add_decomposition_rule(DecompositionRule(SomeGate.__class__, decompose_test1, recognize_test))

    def decompose_test2(cmd):
        qb = cmd.qubits
        H | qb

    result.add_decomposition_rule(DecompositionRule(SomeGateClass, decompose_test2, recognize_test))

    assert len(result.decompositions[SomeGate.__class__.__name__]) == 2
    return result

rule_set = make_decomposition_rule_set()

@pytest.fixture()
def fixture_gate_filter():
    # Filter which doesn't allow SomeGate
    def test_gate_filter_func(self, cmd):
        if cmd.gate == SomeGate:
            return False
        return True

    return _replacer.InstructionFilter(test_gate_filter_func)

def test_auto_replacer_default_chooser(fixture_gate_filter):
    # Test that default decomposition_chooser takes always first rule.
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[_replacer.AutoReplacer(rule_set), fixture_gate_filter],
    )
    assert len(rule_set.decompositions[SomeGate.__class__.__name__]) == 2
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    SomeGate | qb
    eng.flush()
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == X

def test_auto_replacer_decomposition_chooser(fixture_gate_filter):
    # Supply a decomposition chooser which always chooses last rule.
    def test_decomp_chooser(cmd, decomposition_list):
        return decomposition_list[-1]

    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[
            _replacer.AutoReplacer(rule_set, test_decomp_chooser),
            fixture_gate_filter,
        ],
    )
    assert len(rule_set.decompositions[SomeGate.__class__.__name__]) == 2
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    SomeGate | qb
    eng.flush()
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == H

def test_auto_replacer_no_rule_found():
    # Check that exception is thrown if no rule is found
    # For both the cmd and it's inverse (which exists)
    def h_filter(self, cmd):
        if cmd.gate == H:
            return False
        return True

    h_filter = _replacer.InstructionFilter(h_filter)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[_replacer.AutoReplacer(rule_set), h_filter])
    qubit = eng.allocate_qubit()
    with pytest.raises(_replacer.NoGateDecompositionError):
        H | qubit
    eng.flush()

def test_auto_replacer_use_inverse_decomposition():
    # Check that if there is no decomposition for the gate, that
    # AutoReplacer runs the decomposition for the inverse gate in reverse

    # Create test gate and inverse
    class NoMagicGate(BasicGate):
        pass

    class MagicGate(BasicGate):
        def get_inverse(self):
            return NoMagicGate()

    def decompose_no_magic_gate(cmd):
        qb = cmd.qubits
        Rx(0.6) | qb
        H | qb

    def recognize_no_magic_gate(cmd):
        return True

    rule_set.add_decomposition_rule(DecompositionRule(NoMagicGate, decompose_no_magic_gate, recognize_no_magic_gate))

    def magic_filter(self, cmd):
        if cmd.gate == MagicGate():
            return False
        return True

    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[
            _replacer.AutoReplacer(rule_set),
            _replacer.InstructionFilter(magic_filter),
        ],
    )
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    MagicGate() | qb
    eng.flush()
    assert len(backend.received_commands) == 4
    assert backend.received_commands[1].gate == H
    assert backend.received_commands[2].gate == Rx(-0.6)

def test_auto_replacer_adds_tags(fixture_gate_filter):
    # Test that AutoReplacer puts back the tags
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend,
        engine_list=[_replacer.AutoReplacer(rule_set), fixture_gate_filter],
    )
    assert len(rule_set.decompositions[SomeGate.__class__.__name__]) == 2
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    cmd = Command(eng, SomeGate, (qb,))
    cmd.tags = ["AddedTag"]
    eng.send([cmd])
    eng.flush()
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == X
    assert len(backend.received_commands[1].tags) == 1
    assert backend.received_commands[1].tags[0] == "AddedTag"

def test_auto_replacer_searches_parent_class_for_rule():
    class DerivedSomeGate(SomeGateClass):
        pass

    def test_gate_filter_func(self, cmd):
        if cmd.gate == X or cmd.gate == H or isinstance(cmd.gate, ClassicalInstructionGate):
            return True
        return False

    i_filter = _replacer.InstructionFilter(test_gate_filter_func)
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[_replacer.AutoReplacer(rule_set), i_filter])
    qb = eng.allocate_qubit()
    DerivedSomeGate() | qb
    eng.flush()
    received_gate = backend.received_commands[1].gate
    assert received_gate == X or received_gate == H

def test_auto_replacer_priorize_controlstate_rule():
    # Check that when a control state is given and it has negative control,
    # Autoreplacer prioritizes the corresponding decomposition rule before anything else.
    # (Decomposition rule should have name _decompose_controlstate)

    # Create test gate and inverse
    class ControlGate(BasicGate):
        pass

    def _decompose_controlstate(cmd):
        S | cmd.qubits

    def _decompose_random(cmd):
        H | cmd.qubits

    def control_filter(self, cmd):
        if cmd.gate == ControlGate():
            return False
        return True

    rule_set.add_decomposition_rule(DecompositionRule(BasicGate, _decompose_random))

    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend, engine_list=[_replacer.AutoReplacer(rule_set), _replacer.InstructionFilter(control_filter)]
    )
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    ControlGate() | qb
    eng.flush()
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == H

    rule_set.add_decomposition_rule(DecompositionRule(BasicGate, _decompose_controlstate))

    backend = DummyEngine(save_commands=True)
    eng = MainEngine(
        backend=backend, engine_list=[_replacer.AutoReplacer(rule_set), _replacer.InstructionFilter(control_filter)]
    )
    assert len(backend.received_commands) == 0
    qb = eng.allocate_qubit()
    ControlGate() | qb
    eng.flush()
    assert len(backend.received_commands) == 3
    assert backend.received_commands[1].gate == S