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

import matplotlib
import matplotlib.pyplot as plt  # noqa: F401
import pytest

from divya.cengines import MainEngine
from divya.backends import Simulator
from divya.cengines import BasicEngine, DummyEngine
from divya.libs.hist import histogram
from divya.ops import All, AllocateQubitGate, C, FlushGate, H, Measure, X

@pytest.fixture(scope="module")
def matplotlib_setup():
    old_backend = matplotlib.get_backend()
    matplotlib.use('agg')  # avoid showing the histogram plots
    yield
    matplotlib.use(old_backend)

def test_invalid_backend(matplotlib_setup):
    eng = MainEngine(backend=DummyEngine())
    qubit = eng.allocate_qubit()
    eng.flush()

    with pytest.raises(RuntimeError):
        histogram(eng.backend, qubit)

def test_backend_get_probabilities_method(matplotlib_setup):
    class MyBackend(BasicEngine):
        def get_probabilities(self, qureg):
            return {'000': 0.5, '111': 0.5}

        def is_available(self, cmd):
            return True

        def receive(self, command_list):
            for cmd in command_list:
                if not isinstance(cmd.gate, FlushGate):
                    assert isinstance(cmd.gate, AllocateQubitGate)

    eng = MainEngine(backend=MyBackend(), verbose=True)
    qureg = eng.allocate_qureg(3)
    eng.flush()
    _, _, prob = histogram(eng.backend, qureg)
    assert prob['000'] == 0.5
    assert prob['111'] == 0.5

    # NB: avoid throwing exceptions when destroying the MainEngine
    eng.next_engine = DummyEngine()
    eng.next_engine.is_last_engine = True

def test_qubit(matplotlib_setup):
    sim = Simulator()
    eng = MainEngine(sim)
    qubit = eng.allocate_qubit()
    eng.flush()
    _, _, prob = histogram(sim, qubit)
    assert prob["0"] == pytest.approx(1)
    assert prob["1"] == pytest.approx(0)
    H | qubit
    eng.flush()
    _, _, prob = histogram(sim, qubit)
    assert prob["0"] == pytest.approx(0.5)
    Measure | qubit
    eng.flush()
    _, _, prob = histogram(sim, qubit)
    assert prob["0"] == pytest.approx(1) or prob["1"] == pytest.approx(1)

def test_qureg(matplotlib_setup):
    sim = Simulator()
    eng = MainEngine(sim)
    qureg = eng.allocate_qureg(3)
    eng.flush()
    _, _, prob = histogram(sim, qureg)
    assert prob["000"] == pytest.approx(1)
    assert prob["110"] == pytest.approx(0)
    H | qureg[0]
    C(X, 1) | (qureg[0], qureg[1])
    H | qureg[2]
    eng.flush()
    _, _, prob = histogram(sim, qureg)
    assert prob["110"] == pytest.approx(0.25)
    assert prob["100"] == pytest.approx(0)
    All(Measure) | qureg
    eng.flush()
    _, _, prob = histogram(sim, qureg)
    assert (
        prob["000"] == pytest.approx(1)
        or prob["001"] == pytest.approx(1)
        or prob["110"] == pytest.approx(1)
        or prob["111"] == pytest.approx(1)
    )
    assert prob["000"] + prob["001"] + prob["110"] + prob["111"] == pytest.approx(1)

def test_combination(matplotlib_setup):
    sim = Simulator()
    eng = MainEngine(sim)
    qureg = eng.allocate_qureg(2)
    qubit = eng.allocate_qubit()
    eng.flush()
    _, _, prob = histogram(sim, [qureg, qubit])
    assert prob["000"] == pytest.approx(1)
    H | qureg[0]
    C(X, 1) | (qureg[0], qureg[1])
    H | qubit
    Measure | qureg[0]
    eng.flush()
    _, _, prob = histogram(sim, [qureg, qubit])
    assert (prob["000"] == pytest.approx(0.5) and prob["001"] == pytest.approx(0.5)) or (
        prob["110"] == pytest.approx(0.5) and prob["111"] == pytest.approx(0.5)
    )
    assert prob["100"] == pytest.approx(0)
    Measure | qubit

def test_too_many_qubits(matplotlib_setup, capsys):
    sim = Simulator()
    eng = MainEngine(sim)
    qureg = eng.allocate_qureg(6)
    eng.flush()
    l_ref = len(capsys.readouterr().out)
    _, _, prob = histogram(sim, qureg)
    assert len(capsys.readouterr().out) > l_ref
    assert prob["000000"] == pytest.approx(1)
    All(Measure)