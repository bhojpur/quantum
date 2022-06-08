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

"""Tests for libs.revkit._control_function."""

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.libs.revkit import ControlFunctionOracle

# run this test only if RevKit Python module can be loaded
revkit = pytest.importorskip('revkit')

def test_control_function_majority():
    saving_backend = DummyEngine(save_commands=True)
    main_engine = MainEngine(backend=saving_backend, engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()
    qubit2 = main_engine.allocate_qubit()
    qubit3 = main_engine.allocate_qubit()

    ControlFunctionOracle(0xE8) | (qubit0, qubit1, qubit2, qubit3)

    assert len(saving_backend.received_commands) == 7

def test_control_function_majority_from_python():
    dormouse = pytest.importorskip('dormouse')  # noqa: F841

    def maj(a, b, c):
        return (a and b) or (a and c) or (b and c)  # pragma: no cover

    saving_backend = DummyEngine(save_commands=True)
    main_engine = MainEngine(backend=saving_backend, engine_list=[DummyEngine()])

    qubit0 = main_engine.allocate_qubit()
    qubit1 = main_engine.allocate_qubit()
    qubit2 = main_engine.allocate_qubit()
    qubit3 = main_engine.allocate_qubit()

    ControlFunctionOracle(maj) | (qubit0, qubit1, qubit2, qubit3)

def test_control_function_invalid_function():
    main_engine = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])

    qureg = main_engine.allocate_qureg(3)

    with pytest.raises(AttributeError):
        ControlFunctionOracle(-42) | qureg

    with pytest.raises(AttributeError):
        ControlFunctionOracle(0x8E) | qureg

    with pytest.raises(RuntimeError):
        ControlFunctionOracle(0x8, synth=revkit.esopps) | qureg