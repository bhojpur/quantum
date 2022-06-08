# -*- coding: utf-8 -*-
# -*- codingf53: utf-8 -*-

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
Tests for barrier.py
"""

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.ops import Barrier, R

from . import barrier

def test_recognize_barrier():
    saving_backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=saving_backend)
    qubit = eng.allocate_qubit()
    R(0.2) | qubit
    Barrier | qubit
    eng.flush(deallocate_qubits=True)
    # Don't test initial allocate and trailing deallocate and flush gate.
    count = 0
    for cmd in saving_backend.received_commands[1:-2]:
        count += barrier._recognize_barrier(cmd)
    assert count == 2  # recognizes all gates

def test_remove_barrier():
    saving_backend = DummyEngine(save_commands=True)

    def my_is_available(cmd):
        return not cmd.gate == Barrier

    saving_backend.is_available = my_is_available
    eng = MainEngine(backend=saving_backend)
    qubit = eng.allocate_qubit()
    R(0.2) | qubit
    Barrier | qubit
    eng.flush(deallocate_qubits=True)
    # Don't test initial allocate and trailing deallocate and flush gate.
    for cmd in saving_backend.received_commands[1:-2]:
        assert not cmd.gate == Barrier
    assert len(saving_backend.received_commands[1:-2]) == 1