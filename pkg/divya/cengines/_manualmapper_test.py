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

"""Tests for divya.cengines._manualmapper.py."""

from divya import MainEngine
from divya.cengines import DummyEngine, ManualMapper
from divya.meta import LogicalQubitIDTag
from divya.ops import All, H, Measure

def test_manualmapper_mapping():
    backend = DummyEngine(save_commands=True)

    def mapping(qubit_id):
        return (qubit_id + 1) & 1

    eng = MainEngine(backend=backend, engine_list=[ManualMapper(mapping)])
    qb0 = eng.allocate_qubit()
    qb1 = eng.allocate_qubit()
    H | qb0
    H | qb1
    All(Measure) | (qb0 + qb1)
    eng.flush()

    num_measurements = 0
    for cmd in backend.received_commands:
        if cmd.gate == Measure:
            tag = LogicalQubitIDTag(mapping(cmd.qubits[0][0].id))
            assert tag in cmd.tags
            wrong_tag = LogicalQubitIDTag(cmd.qubits[0][0].id)
            assert wrong_tag not in cmd.tags
            num_measurements += 1
    assert num_measurements == 2