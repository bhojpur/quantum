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
Tests for divya.backends.circuits._drawer.py.
"""

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine
from divya.ops import CNOT, BasicGate, Command, H, Measure, Rx, Swap, X
from divya.types import WeakQubitRef

from . import _drawer_matplotlib as _drawer
from ._drawer_matplotlib import CircuitDrawerMatplotlib

def test_drawer_measurement():
    drawer = CircuitDrawerMatplotlib(default_measure=0)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 0

    drawer = CircuitDrawerMatplotlib(default_measure=1)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()
    Measure | qubit
    assert int(qubit) == 1

    drawer = CircuitDrawerMatplotlib(accept_input=True)
    eng = MainEngine(drawer, [])
    qubit = eng.allocate_qubit()

    old_input = _drawer.input

    _drawer.input = lambda x: '1'
    Measure | qubit
    assert int(qubit) == 1
    _drawer.input = old_input

    qb1 = WeakQubitRef(engine=eng, idx=1)
    qb2 = WeakQubitRef(engine=eng, idx=2)
    with pytest.raises(ValueError):
        eng.backend._process(Command(engine=eng, gate=Measure, qubits=([qb1],), controls=[qb2]))

class MockEngine(object):
    def is_available(self, cmd):
        self.cmd = cmd
        self.called = True
        return False

def test_drawer_isavailable():
    drawer = CircuitDrawerMatplotlib()
    drawer.is_last_engine = True

    qb0 = WeakQubitRef(None, 0)
    qb1 = WeakQubitRef(None, 1)
    qb2 = WeakQubitRef(None, 2)
    qb3 = WeakQubitRef(None, 3)

    for gate in (X, Rx(1.0)):
        for qubits in (([qb0],), ([qb0, qb1],), ([qb0, qb1, qb2],)):
            print(qubits)
            cmd = Command(None, gate, qubits)
            assert drawer.is_available(cmd)

    cmd0 = Command(None, X, ([qb0],))
    cmd1 = Command(None, Swap, ([qb0], [qb1]))
    cmd2 = Command(None, Swap, ([qb0], [qb1]), [qb2])
    cmd3 = Command(None, Swap, ([qb0], [qb1]), [qb2, qb3])

    assert drawer.is_available(cmd1)
    assert drawer.is_available(cmd2)
    assert drawer.is_available(cmd3)

    mock_engine = MockEngine()
    mock_engine.called = False
    drawer.is_last_engine = False
    drawer.next_engine = mock_engine

    assert not drawer.is_available(cmd0)
    assert mock_engine.called
    assert mock_engine.cmd is cmd0

    assert not drawer.is_available(cmd1)
    assert mock_engine.called
    assert mock_engine.cmd is cmd1

def _draw_subst(qubit_lines, qubit_labels=None, drawing_order=None, **kwargs):
    return qubit_lines

class MyGate(BasicGate):
    def __init__(self, *args):
        super().__init__()
        self.params = args

    def __str__(self):
        param_str = '{}'.format(self.params[0])
        for param in self.params[1:]:
            param_str += ',{}'.format(param)
        return str(self.__class__.__name__) + "(" + param_str + ")"

def test_drawer_draw():
    old_draw = _drawer.to_draw
    _drawer.to_draw = _draw_subst

    backend = DummyEngine()

    drawer = CircuitDrawerMatplotlib()

    eng = MainEngine(backend, [drawer])
    qureg = eng.allocate_qureg(3)
    H | qureg[1]
    H | qureg[0]
    X | qureg[0]
    Rx(1) | qureg[1]
    CNOT | (qureg[0], qureg[1])
    Swap | (qureg[0], qureg[1])
    MyGate(1.2) | qureg[2]
    MyGate(1.23456789) | qureg[2]
    MyGate(1.23456789, 2.3456789) | qureg[2]
    MyGate(1.23456789, 'aaaaaaaa', 'bbb', 2.34) | qureg[2]
    X | qureg[0]

    qubit_lines = drawer.draw()

    assert qubit_lines == {
        0: [('H', [0], []), ('X', [0], []), None, ('Swap', [0, 1], []), ('X', [0], [])],
        1: [('H', [1], []), ('Rx(1.00)', [1], []), ('X', [1], [0]), None, None],
        2: [
            ('MyGate(1.20)', [2], []),
            ('MyGate(1.23)', [2], []),
            ('MyGate(1.23,2.35)', [2], []),
            ('MyGate(1.23,aaaaa...,bbb,2.34)', [2], []),
            None,
        ],
    }

    _drawer.to_draw = old_draw