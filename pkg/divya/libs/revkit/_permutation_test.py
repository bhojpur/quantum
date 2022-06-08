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

"""Tests for libs.revkit._permutation."""

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.libs.revkit import PermutationOracle

# run this test only if RevKit Python module can be loaded
revkit = pytest.importorskip('revkit')

def test_basic_permutation():
    saving_backend = DummyEngine(save_commands=True)
    main_engine = MainEngine(backend=saving_backend, engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()

    PermutationOracle([0, 2, 1, 3]) | (qubit0, qubit1)

    assert len(saving_backend.received_commands) == 5

def test_invalid_permutation():
    main_engine = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()

    with pytest.raises(AttributeError):
        PermutationOracle([1, 2, 3, 4]) | (qubit0, qubit1)

    with pytest.raises(AttributeError):
        PermutationOracle([0, 2, 3, 4]) | (qubit0, qubit1)

    with pytest.raises(AttributeError):
        PermutationOracle([0, 1, 1, 2]) | (qubit0, qubit1)

    with pytest.raises(AttributeError):
        PermutationOracle([0, 1, 2]) | (qubit0, qubit1)

    with pytest.raises(AttributeError):
        PermutationOracle([0, 1, 2, 3, 4]) | (qubit0, qubit1)

def test_synthesis_with_adjusted_tbs():
    saving_backend = DummyEngine(save_commands=True)
    main_engine = MainEngine(backend=saving_backend, engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()

    def synth():
        import revkit

        return revkit.tbs()

    PermutationOracle([0, 2, 1, 3], synth=synth) | (qubit0, qubit1)

    assert len(saving_backend.received_commands) == 5

def test_synthesis_with_synthesis_script():
    saving_backend = DummyEngine(save_commands=True)
    main_engine = MainEngine(backend=saving_backend, engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()

    def synth():
        import revkit

        revkit.tbs()

    PermutationOracle([0, 2, 1, 3], synth=synth) | (qubit0, qubit1)

    assert len(saving_backend.received_commands) == 5