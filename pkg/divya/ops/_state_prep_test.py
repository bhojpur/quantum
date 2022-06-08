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

"""Tests for divya.ops._state_prep."""

from divya.ops import X, _state_prep

def test_equality_and_hash():
    gate1 = _state_prep.StatePreparation([0.5, -0.5, 0.5, -0.5])
    gate2 = _state_prep.StatePreparation([0.5, -0.5, 0.5, -0.5])
    gate3 = _state_prep.StatePreparation([0.5, -0.5, 0.5, 0.5])
    assert gate1 == gate2
    assert hash(gate1) == hash(gate2)
    assert gate1 != gate3
    assert gate1 != X

def test_str():
    gate1 = _state_prep.StatePreparation([0, 1])
    assert str(gate1) == "StatePreparation"