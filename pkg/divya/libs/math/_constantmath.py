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

"""Module containing constant math quantum operations."""

import math

try:
    from math import gcd
except ImportError:  # pragma: no cover
    from fractions import gcd

from divya.meta import Compute, Control, CustomUncompute, Uncompute
from divya.ops import CNOT, QFT, R, Swap, X

from ._gates import AddConstant, AddConstantModN, SubConstant, SubConstantModN

# Draper's addition by constant https://arxiv.org/abs/quant-ph/0008033
def add_constant(eng, constant, quint):
    """
    Add a classical constant c to the quantum integer (qureg) quint using Draper addition.

    Note:
        Uses the Fourier-transform adder from https://arxiv.org/abs/quant-ph/0008033.
    """
    with Compute(eng):
        QFT | quint

    for i, qubit in enumerate(quint):
        for j in range(i, -1, -1):
            if (constant >> j) & 1:
                R(math.pi / (1 << (i - j))) | qubit

    Uncompute(eng)

# Modular adder by Beauregard https://arxiv.org/abs/quant-ph/0205095
def add_constant_modN(eng, constant, N, quint):  # pylint: disable=invalid-name
    """
    Add a classical constant c to a quantum integer (qureg) quint modulo N using Draper addition.

    This function uses Draper addition and the construction from https://arxiv.org/abs/quant-ph/0205095.
    """
    if constant < 0 or constant > N:
        raise ValueError('Pre-condition failed: 0 <= constant < N')

    AddConstant(constant) | quint

    with Compute(eng):
        SubConstant(N) | quint
        ancilla = eng.allocate_qubit()
        CNOT | (quint[-1], ancilla)
        with Control(eng, ancilla):
            AddConstant(N) | quint

    SubConstant(constant) | quint

    with CustomUncompute(eng):
        X | quint[-1]
        CNOT | (quint[-1], ancilla)
        X | quint[-1]
        del ancilla

    AddConstant(constant) | quint

# Modular multiplication by modular addition & shift, followed by uncompute
# from https://arxiv.org/abs/quant-ph/0205095
def mul_by_constant_modN(eng, constant, N, quint_in):  # pylint: disable=invalid-name
    """
    Multiply a quantum integer by a classical number a modulo N.

    i.e.,

    |x> -> |a*x mod N>

    (only works if a and N are relative primes, otherwise the modular inverse
    does not exist).
    """
    if constant < 0 or constant > N:
        raise ValueError('Pre-condition failed: 0 <= constant < N')
    if gcd(constant, N) != 1:
        raise ValueError('Pre-condition failed: gcd(constant, N) == 1')

    n_qubits = len(quint_in)
    quint_out = eng.allocate_qureg(n_qubits + 1)

    for i in range(n_qubits):
        with Control(eng, quint_in[i]):
            AddConstantModN((constant << i) % N, N) | quint_out

    for i in range(n_qubits):
        Swap | (quint_out[i], quint_in[i])

    cinv = inv_mod_N(constant, N)

    for i in range(n_qubits):
        with Control(eng, quint_in[i]):
            SubConstantModN((cinv << i) % N, N) | quint_out
    del quint_out

def inv_mod_N(a, N):  # pylint: disable=invalid-name
    """Calculate the inverse of a modulo N."""
    # pylint: disable=invalid-name
    s = 0
    old_s = 1
    r = N
    old_r = a
    while r != 0:
        q = int(old_r / r)
        tmp = r
        r = old_r - q * r
        old_r = tmp
        tmp = s
        s = old_s - q * s
        old_s = tmp
    return (old_s + N) % N