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

"""Tests for _conversion.py."""
from __future__ import absolute_import

import copy
import numpy
import unittest

from maya.ops import (FermionOperator,
                          InteractionOperator,
                          normal_ordered,
                          number_operator)
from maya.ops._interaction_operator import InteractionOperatorError
from maya.transforms import *
from maya.utils import *

from divya.ops import QubitOperator

class GetInteractionOperatorTest(unittest.TestCase):

    def test_get_molecular_operator(self):
        coefficient = 3.
        operators = ((2, 1), (3, 0), (0, 0), (3, 1))
        op = FermionOperator(operators, coefficient)

        molecular_operator = get_interaction_operator(op)
        fermion_operator = get_fermion_operator(molecular_operator)
        fermion_operator = normal_ordered(fermion_operator)
        self.assertTrue(normal_ordered(op).isclose(fermion_operator))

    def test_get_interaction_operator_bad_input(self):
        with self.assertRaises(TypeError):
            get_interaction_operator('3')

    def test_get_interaction_operator_too_few_qubits(self):
        with self.assertRaises(ValueError):
            get_interaction_operator(FermionOperator('3^ 2^ 1 0'), 3)

    def test_get_interaction_operator_bad_1body_term(self):
        with self.assertRaises(InteractionOperatorError):
            get_interaction_operator(FermionOperator('1^ 0^'))

    def test_get_interaction_operator_bad_2body_term(self):
        with self.assertRaises(InteractionOperatorError):
            get_interaction_operator(FermionOperator('3^ 2 1 0'))

    def test_get_interaction_operator_nonmolecular_term(self):
        with self.assertRaises(InteractionOperatorError):
            get_interaction_operator(FermionOperator('3^ 2 1'))


class GetSparseOperatorQubitTest(unittest.TestCase):

    def test_sparse_matrix_Y(self):
        term = QubitOperator(((0, 'Y'),))
        sparse_operator = get_sparse_operator(term)
        self.assertEqual(list(sparse_operator.data), [1j, -1j])
        self.assertEqual(list(sparse_operator.indices), [1, 0])
        self.assertTrue(is_hermitian(sparse_operator))

    def test_sparse_matrix_ZX(self):
        coefficient = 2.
        operators = ((0, 'Z'), (1, 'X'))
        term = QubitOperator(operators, coefficient)
        sparse_operator = get_sparse_operator(term)
        self.assertEqual(list(sparse_operator.data), [2., 2., -2., -2.])
        self.assertEqual(list(sparse_operator.indices), [1, 0, 3, 2])
        self.assertTrue(is_hermitian(sparse_operator))

    def test_sparse_matrix_ZIZ(self):
        operators = ((0, 'Z'), (2, 'Z'))
        term = QubitOperator(operators)
        sparse_operator = get_sparse_operator(term)
        self.assertEqual(list(sparse_operator.data),
                         [1, -1, 1, -1, -1, 1, -1, 1])
        self.assertEqual(list(sparse_operator.indices), list(range(8)))
        self.assertTrue(is_hermitian(sparse_operator))

    def test_sparse_matrix_combo(self):
        qop = (QubitOperator(((0, 'Y'), (1, 'X')), -0.1j) +
               QubitOperator(((0, 'X'), (1, 'Z')), 3. + 2.j))
        sparse_operator = get_sparse_operator(qop)

        self.assertEqual(list(sparse_operator.data),
                         [3 + 2j, 0.1, 0.1, -3 - 2j,
                          3 + 2j, -0.1, -0.1, -3 - 2j])
        self.assertEqual(list(sparse_operator.indices),
                         [2, 3, 2, 3, 0, 1, 0, 1])

    def test_sparse_matrix_zero_1qubit(self):
        sparse_operator = get_sparse_operator(QubitOperator((), 0.0), 1)
        sparse_operator.eliminate_zeros()
        self.assertEqual(len(list(sparse_operator.data)), 0)
        self.assertEqual(sparse_operator.shape, (2, 2))

    def test_sparse_matrix_zero_5qubit(self):
        sparse_operator = get_sparse_operator(QubitOperator((), 0.0), 5)
        sparse_operator.eliminate_zeros()
        self.assertEqual(len(list(sparse_operator.data)), 0)
        self.assertEqual(sparse_operator.shape, (32, 32))

    def test_sparse_matrix_identity_1qubit(self):
        sparse_operator = get_sparse_operator(QubitOperator(()), 1)
        self.assertEqual(list(sparse_operator.data), [1] * 2)
        self.assertEqual(sparse_operator.shape, (2, 2))

    def test_sparse_matrix_identity_5qubit(self):
        sparse_operator = get_sparse_operator(QubitOperator(()), 5)
        self.assertEqual(list(sparse_operator.data), [1] * 32)
        self.assertEqual(sparse_operator.shape, (32, 32))

    def test_sparse_matrix_linearity(self):
        identity = QubitOperator(())
        zzzz = QubitOperator(tuple((i, 'Z') for i in range(4)), 1.0)

        sparse1 = get_sparse_operator(identity + zzzz)
        sparse2 = get_sparse_operator(identity, 4) + get_sparse_operator(zzzz)

        self.assertEqual(list(sparse1.data), [2] * 8)
        self.assertEqual(list(sparse1.indices),
                         [0, 3, 5, 6, 9, 10, 12, 15])
        self.assertEqual(list(sparse2.data), [2] * 8)
        self.assertEqual(list(sparse2.indices),
                         [0, 3, 5, 6, 9, 10, 12, 15])


class GetSparseOperatorFermionTest(unittest.TestCase):

    def test_sparse_matrix_zero_n_qubit(self):
        sparse_operator = get_sparse_operator(FermionOperator.zero(), 4)
        sparse_operator.eliminate_zeros()
        self.assertEqual(len(list(sparse_operator.data)), 0)
        self.assertEqual(sparse_operator.shape, (16, 16))