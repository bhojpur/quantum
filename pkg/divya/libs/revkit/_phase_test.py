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

"""Tests for libs.revkit._phase."""

import numpy as np
import pytest

from divya import MainEngine
from divya.backends import Simulator
from divya.cengines import DummyEngine
from divya.libs.revkit import PhaseOracle
from divya.ops import All, H, Measure

# run this test only if RevKit Python module can be loaded
revkit = pytest.importorskip('revkit')

def test_phase_majority():
    sim = Simulator()
    main_engine = MainEngine(sim)

    qureg = main_engine.allocate_qureg(3)
    All(H) | qureg
    PhaseOracle(0xE8) | qureg

    main_engine.flush()

    assert np.array_equal(np.sign(sim.cheat()[1]), [1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0])
    All(Measure) | qureg

def test_phase_majority_from_python():
    dormouse = pytest.importorskip('dormouse')  # noqa: F841

    def maj(a, b, c):
        return (a and b) or (a and c) or (b and c)  # pragma: no cover

    sim = Simulator()
    main_engine = MainEngine(sim)

    qureg = main_engine.allocate_qureg(3)
    All(H) | qureg
    PhaseOracle(maj) | qureg

    main_engine.flush()

    assert np.array_equal(np.sign(sim.cheat()[1]), [1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, -1.0])
    All(Measure) | qureg

def test_phase_invalid_function():
    main_engine = MainEngine(backend=DummyEngine(), engine_list=[DummyEngine()])

    qureg = main_engine.allocate_qureg(3)

    with pytest.raises(AttributeError):
        PhaseOracle(-42) | qureg

    with pytest.raises(AttributeError):
        PhaseOracle(0xCAFE) | qureg

    with pytest.raises(RuntimeError):
        PhaseOracle(0x8E, synth=lambda: revkit.esopbs()) | qureg