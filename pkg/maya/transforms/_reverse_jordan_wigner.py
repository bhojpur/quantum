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

"""Reverse Jordan-Wigner transform on QubitOperators."""
from __future__ import absolute_import

import copy

from maya.ops import (FermionOperator,
                          number_operator)
from maya.utils import count_qubits

from divya.ops import QubitOperator


def reverse_jordan_wigner(qubit_operator, n_qubits=None):
    """Transforms a QubitOperator into a FermionOperator using the
    Jordan-Wigner transform.

    Operators are mapped as follows:
    Z_j -> I - 2 a^\dagger_j a_j
    X_j -> (a^\dagger_j + a_j) Z_{j-1} Z_{j-2} .. Z_0
    Y_j -> i (a^\dagger_j - a_j) Z_{j-1} Z_{j-2} .. Z_0

    Args:
        qubit_operator: the QubitOperator to be transformed.
        n_qubits: the number of qubits term acts on. If not set, defaults
                to the maximum qubit number acted on by term.

    Returns:
        transformed_term: An instance of the FermionOperator class.

    Raises:
        TypeError: Input must be a QubitOperator.
        TypeError: Invalid number of qubits specified.
        TypeError: Pauli operators must be X, Y or Z.
    """
    if not isinstance(qubit_operator, QubitOperator):
        raise TypeError('Input must be a QubitOperator.')
    if n_qubits is None:
        n_qubits = count_qubits(qubit_operator)
    if n_qubits < count_qubits(qubit_operator):
        raise ValueError('Invalid number of qubits specified.')

    # Loop through terms.
    transformed_operator = FermionOperator()
    for term in qubit_operator.terms:
        transformed_term = FermionOperator(())
        if term:
            working_term = QubitOperator(term)
            pauli_operator = term[-1]
            while pauli_operator is not None:

                # Handle Pauli Z.
                if pauli_operator[1] == 'Z':
                    transformed_pauli = FermionOperator(
                        ()) + number_operator(n_qubits, pauli_operator[0], -2.)

                # Handle Pauli X and Y.
                else:
                    raising_term = FermionOperator(((pauli_operator[0], 1),))
                    lowering_term = FermionOperator(((pauli_operator[0], 0),))
                    if pauli_operator[1] == 'Y':
                        raising_term *= 1.j
                        lowering_term *= -1.j

                    transformed_pauli = raising_term + lowering_term

                    # Account for the phase terms.
                    for j in reversed(range(pauli_operator[0])):
                        z_term = QubitOperator(((j, 'Z'),))
                        working_term = z_term * working_term
                    term_key = list(working_term.terms)[0]
                    transformed_pauli *= working_term.terms[term_key]
                    working_term.terms[list(working_term.terms)[0]] = 1.

                # Get next non-identity operator acting below 'working_qubit'.
                assert len(working_term.terms) == 1
                working_qubit = pauli_operator[0] - 1
                for working_operator in reversed(list(working_term.terms)[0]):
                    if working_operator[0] <= working_qubit:
                        pauli_operator = working_operator
                        break
                    else:
                        pauli_operator = None

                # Multiply term by transformed operator.
                transformed_term *= transformed_pauli

        # Account for overall coefficient
        transformed_term *= qubit_operator.terms[term]
        transformed_operator += transformed_term
    return transformed_operator