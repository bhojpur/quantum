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

"Tests for divya.setups.decompositions.phaseestimation.py."

import cmath

import numpy as np
import pytest
from flaky import flaky

import divya.setups.decompositions.stateprep2cnot as stateprep2cnot
import divya.setups.decompositions.uniformlycontrolledr2cnot as ucr2cnot
from divya.backends import Simulator
from divya.cengines import AutoReplacer, DecompositionRuleSet, MainEngine
from divya.ops import CNOT, QPE, All, H, Measure, Ph, StatePreparation, Tensor, X
from divya.setups.decompositions import phaseestimation as pe
from divya.setups.decompositions import qft2crandhadamard as dqft

@flaky(max_runs=5, min_passes=2)
def test_simple_test_X_eigenvectors():
    rule_set = DecompositionRuleSet(modules=[pe, dqft])
    eng = MainEngine(
        backend=Simulator(),
        engine_list=[
            AutoReplacer(rule_set),
        ],
    )
    N = 150
    results = np.array([])
    for i in range(N):
        autovector = eng.allocate_qureg(1)
        X | autovector
        H | autovector
        unit = X
        ancillas = eng.allocate_qureg(1)
        QPE(unit) | (ancillas, autovector)
        All(Measure) | ancillas
        fasebinlist = [int(q) for q in ancillas]
        fasebin = ''.join(str(j) for j in fasebinlist)
        faseint = int(fasebin, 2)
        phase = faseint / (2.0 ** (len(ancillas)))
        results = np.append(results, phase)
        All(Measure) | autovector
        eng.flush()

    num_phase = (results == 0.5).sum()
    assert num_phase / N >= 0.35, "Statistics phase calculation are not correct (%f vs. %f)" % (
        num_phase / N,
        0.35,
    )

@flaky(max_runs=5, min_passes=2)
def test_Ph_eigenvectors():
    rule_set = DecompositionRuleSet(modules=[pe, dqft])
    eng = MainEngine(
        backend=Simulator(),
        engine_list=[
            AutoReplacer(rule_set),
        ],
    )
    N = 150
    results = np.array([])
    for i in range(N):
        autovector = eng.allocate_qureg(1)
        theta = cmath.pi * 2.0 * 0.125
        unit = Ph(theta)
        ancillas = eng.allocate_qureg(3)
        QPE(unit) | (ancillas, autovector)
        All(Measure) | ancillas
        fasebinlist = [int(q) for q in ancillas]
        fasebin = ''.join(str(j) for j in fasebinlist)
        faseint = int(fasebin, 2)
        phase = faseint / (2.0 ** (len(ancillas)))
        results = np.append(results, phase)
        All(Measure) | autovector
        eng.flush()

    num_phase = (results == 0.125).sum()
    assert num_phase / N >= 0.35, "Statistics phase calculation are not correct (%f vs. %f)" % (
        num_phase / N,
        0.35,
    )

def two_qubit_gate(system_q, time):
    CNOT | (system_q[0], system_q[1])
    Ph(2.0 * cmath.pi * (time * 0.125)) | system_q[1]
    CNOT | (system_q[0], system_q[1])

@flaky(max_runs=5, min_passes=2)
def test_2qubitsPh_andfunction_eigenvectors():
    rule_set = DecompositionRuleSet(modules=[pe, dqft])
    eng = MainEngine(
        backend=Simulator(),
        engine_list=[
            AutoReplacer(rule_set),
        ],
    )
    N = 150
    results = np.array([])
    for i in range(N):
        autovector = eng.allocate_qureg(2)
        X | autovector[0]
        ancillas = eng.allocate_qureg(3)
        QPE(two_qubit_gate) | (ancillas, autovector)
        All(Measure) | ancillas
        fasebinlist = [int(q) for q in ancillas]
        fasebin = ''.join(str(j) for j in fasebinlist)
        faseint = int(fasebin, 2)
        phase = faseint / (2.0 ** (len(ancillas)))
        results = np.append(results, phase)
        All(Measure) | autovector
        eng.flush()

    num_phase = (results == 0.125).sum()
    assert num_phase / N >= 0.34, "Statistics phase calculation are not correct (%f vs. %f)" % (
        num_phase / N,
        0.34,
    )

def test_X_no_eigenvectors():
    rule_set = DecompositionRuleSet(modules=[pe, dqft, stateprep2cnot, ucr2cnot])
    eng = MainEngine(
        backend=Simulator(),
        engine_list=[
            AutoReplacer(rule_set),
        ],
    )
    N = 100
    results = np.array([])
    results_plus = np.array([])
    results_minus = np.array([])
    for i in range(N):
        autovector = eng.allocate_qureg(1)
        amplitude0 = (np.sqrt(2) + np.sqrt(6)) / 4.0
        amplitude1 = (np.sqrt(2) - np.sqrt(6)) / 4.0
        StatePreparation([amplitude0, amplitude1]) | autovector
        unit = X
        ancillas = eng.allocate_qureg(1)
        QPE(unit) | (ancillas, autovector)
        All(Measure) | ancillas
        fasebinlist = [int(q) for q in ancillas]
        fasebin = ''.join(str(j) for j in fasebinlist)
        faseint = int(fasebin, 2)
        phase = faseint / (2.0 ** (len(ancillas)))
        results = np.append(results, phase)
        Tensor(H) | autovector
        if np.allclose(phase, 0.0, rtol=1e-1):
            results_plus = np.append(results_plus, phase)
            All(Measure) | autovector
            autovector_result = int(autovector)
            assert autovector_result == 0
        elif np.allclose(phase, 0.5, rtol=1e-1):
            results_minus = np.append(results_minus, phase)
            All(Measure) | autovector
            autovector_result = int(autovector)
            assert autovector_result == 1
        eng.flush()

    total = len(results_plus) + len(results_minus)
    plus_probability = len(results_plus) / N
    assert total == pytest.approx(N, abs=5)
    assert plus_probability == pytest.approx(
        1.0 / 4.0, abs=1e-1
    ), "Statistics on |+> probability are not correct (%f vs. %f)" % (
        plus_probability,
        1.0 / 4.0,
    )

def test_string():
    unit = X
    gate = QPE(unit)
    assert str(gate) == "QPE(X)"