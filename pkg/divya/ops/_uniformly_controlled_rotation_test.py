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

"""Tests for divya.ops._uniformly_controlled_rotation."""
import math

import pytest

from divya.ops import Rx
from divya.ops import _uniformly_controlled_rotation as ucr

from ._basics import NotMergeable

@pytest.mark.parametrize("gate_class", [ucr.UniformlyControlledRy, ucr.UniformlyControlledRz])
def test_init_rounding(gate_class):
    gate = gate_class([0.1 + 4 * math.pi, -1e-14])
    assert gate.angles == [0.1, 0.0]

@pytest.mark.parametrize("gate_class", [ucr.UniformlyControlledRy, ucr.UniformlyControlledRz])
def test_get_inverse(gate_class):
    gate = gate_class([0.1, 0.2, 0.3, 0.4])
    inverse = gate.get_inverse()
    assert inverse == gate_class([-0.1, -0.2, -0.3, -0.4])

@pytest.mark.parametrize("gate_class", [ucr.UniformlyControlledRy, ucr.UniformlyControlledRz])
def test_get_merged(gate_class):
    gate1 = gate_class([0.1, 0.2, 0.3, 0.4])
    gate2 = gate_class([0.1, 0.2, 0.3, 0.4])
    merged_gate = gate1.get_merged(gate2)
    assert merged_gate == gate_class([0.2, 0.4, 0.6, 0.8])
    with pytest.raises(NotMergeable):
        gate1.get_merged(Rx(0.1))

def test_str_and_hash():
    gate1 = ucr.UniformlyControlledRy([0.1, 0.2, 0.3, 0.4])
    gate2 = ucr.UniformlyControlledRz([0.1, 0.2, 0.3, 0.4])
    assert str(gate1) == "UniformlyControlledRy([0.1, 0.2, 0.3, 0.4])"
    assert str(gate2) == "UniformlyControlledRz([0.1, 0.2, 0.3, 0.4])"
    assert hash(gate1) == hash("UniformlyControlledRy([0.1, 0.2, 0.3, 0.4])")
    assert hash(gate2) == hash("UniformlyControlledRz([0.1, 0.2, 0.3, 0.4])")

@pytest.mark.parametrize("gate_class", [ucr.UniformlyControlledRy, ucr.UniformlyControlledRz])
def test_equality(gate_class):
    gate1 = gate_class([0.1, 0.2])
    gate2 = gate_class([0.1, 0.2 + 1e-14])
    assert gate1 == gate2
    gate3 = gate_class([0.1, 0.2, 0.1, 0.2])
    assert gate2 != gate3
    gate4 = ucr.UniformlyControlledRz([0.1, 0.2])
    gate5 = ucr.UniformlyControlledRy([0.1, 0.2])
    assert gate4 != gate5
    assert not gate5 == gate4