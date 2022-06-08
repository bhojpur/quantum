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

from . import (
    amplitudeamplification,
    arb1qubit2rzandry,
    barrier,
    carb1qubit2cnotrzandry,
    cnot2cz,
    cnot2rxx,
    cnu2toffoliandcu,
    controlstate,
    crz2cxandrz,
    entangle,
    globalphase,
    h2rx,
    ph2r,
    phaseestimation,
    qft2crandhadamard,
    qubitop2onequbit,
    r2rzandph,
    rx2rz,
    ry2rz,
    rz2rx,
    sqrtswap2cnot,
    stateprep2cnot,
    swap2cnot,
    time_evolution,
    toffoli2cnotandtgate,
    uniformlycontrolledr2cnot,
)

all_defined_decomposition_rules = [
    rule
    for module in [
        arb1qubit2rzandry,
        barrier,
        carb1qubit2cnotrzandry,
        crz2cxandrz,
        cnot2rxx,
        cnot2cz,
        cnu2toffoliandcu,
        controlstate,
        entangle,
        globalphase,
        h2rx,
        ph2r,
        qubitop2onequbit,
        qft2crandhadamard,
        r2rzandph,
        rx2rz,
        ry2rz,
        rz2rx,
        sqrtswap2cnot,
        stateprep2cnot,
        swap2cnot,
        toffoli2cnotandtgate,
        time_evolution,
        uniformlycontrolledr2cnot,
        phaseestimation,
        amplitudeamplification,
    ]
    for rule in module.all_defined_decomposition_rules
]