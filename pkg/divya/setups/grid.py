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
A setup to compile to qubits placed in 2-D grid.

It provides the `engine_list` for the `MainEngine`. This engine list contains an AutoReplacer with most of the gate
decompositions of Bhojpur Quantum, which are used to decompose a circuit into only two qubit gates and arbitrary single qubit
gates. Bhojpur Quantum's GridMapper is then used to introduce the necessary Swap operations to route interacting qubits next
to each other.  This setup allows to choose the final gate set (with some limitations).
"""

from divya.cengines import GridMapper
from divya.ops import CNOT, Swap

from ._utils import get_engine_list_linear_grid_base

def get_engine_list(num_rows, num_columns, one_qubit_gates="any", two_qubit_gates=(CNOT, Swap)):
    """
    Return an engine list to compile to a 2-D grid of qubits.

    Note:
        If you choose a new gate set for which the compiler does not yet have standard rules, it raises an
        `NoGateDecompositionError` or a `RuntimeError: maximum recursion depth exceeded...`. Also note that even the
        gate sets which work might not yet be optimized. So make sure to double check and potentially extend the
        decomposition rules.  This implemention currently requires that the one qubit gates must contain Rz and at
        least one of {Ry(best), Rx, H} and the two qubit gate must contain CNOT (recommended) or CZ.

    Note:
        Classical instructions gates such as e.g. Flush and Measure are automatically allowed.

    Example:
        get_engine_list(num_rows=2, num_columns=3,
                        one_qubit_gates=(Rz, Ry, Rx, H),
                        two_qubit_gates=(CNOT,))

    Args:
        num_rows(int): Number of rows in the grid
        num_columns(int): Number of columns in the grid.
        one_qubit_gates: "any" allows any one qubit gate, otherwise provide a tuple of the allowed gates. If the gates
                         are instances of a class (e.g. X), it allows all gates which are equal to it. If the gate is
                         a class (Rz), it allows all instances of this class. Default is "any"
        two_qubit_gates: "any" allows any two qubit gate, otherwise provide a tuple of the allowed gates. If the gates
                         are instances of a class (e.g. CNOT), it allows all gates which are equal to it. If the gate
                         is a class, it allows all instances of this class.  Default is (CNOT, Swap).
    Raises:
        TypeError: If input is for the gates is not "any" or a tuple.

    Returns:
        A list of suitable compiler engines.
    """
    return get_engine_list_linear_grid_base(
        GridMapper(num_rows=num_rows, num_columns=num_columns), one_qubit_gates, two_qubit_gates
    )