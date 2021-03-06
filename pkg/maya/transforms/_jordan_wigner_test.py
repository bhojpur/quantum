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

"""Tests  _jordan_wigner.py."""
from __future__ import absolute_import
import numpy

import unittest

from maya.ops import (FermionOperator,
                          hermitian_conjugated,
                          InteractionOperator,
                          normal_ordered,
                          number_operator)
from maya.transforms import (get_interaction_operator,
                                 reverse_jordan_wigner)
from maya.transforms._jordan_wigner import (jordan_wigner,
                                                jordan_wigner_one_body,
                                                jordan_wigner_two_body,
                                                jordan_wigner_interaction_op)

from divya.ops import QubitOperator


class JordanWignerTransformTest(unittest.TestCase):
    def setUp(self):
        self.n_qubits = 5

    def test_bad_input(self):
        with self.assertRaises(TypeError):
            jordan_wigner(3)

    def test_transm_raise3(self):
        raising = jordan_wigner(FermionOperator(((3, 1),)))
        self.assertEqual(len(raising.terms), 2)

        correct_operators_x = ((0, 'Z'), (1, 'Z'), (2, 'Z'), (3, 'X'))
        correct_operators_y = ((0, 'Z'), (1, 'Z'), (2, 'Z'), (3, 'Y'))
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, -0.5j)

        self.assertEqual(raising.terms[correct_operators_x], 0.5)
        self.assertEqual(raising.terms[correct_operators_y], -0.5j)
        self.assertTrue(raising.isclose(qtermx + qtermy))

    def test_transm_raise1(self):
        raising = jordan_wigner(FermionOperator(((1, 1),)))

        correct_operators_x = ((0, 'Z'), (1, 'X'))
        correct_operators_y = ((0, 'Z'), (1, 'Y'))
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, -0.5j)

        self.assertEqual(raising.terms[correct_operators_x], 0.5)
        self.assertEqual(raising.terms[correct_operators_y], -0.5j)
        self.assertTrue(raising.isclose(qtermx + qtermy))

    def test_transm_lower3(self):
        lowering = jordan_wigner(FermionOperator(((3, 0),)))

        correct_operators_x = ((0, 'Z'), (1, 'Z'), (2, 'Z'), (3, 'X'))
        correct_operators_y = ((0, 'Z'), (1, 'Z'), (2, 'Z'), (3, 'Y'))
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, 0.5j)

        self.assertEqual(lowering.terms[correct_operators_x], 0.5)
        self.assertEqual(lowering.terms[correct_operators_y], 0.5j)
        self.assertTrue(lowering.isclose(qtermx + qtermy))

    def test_transm_lower2(self):
        lowering = jordan_wigner(FermionOperator(((2, 0),)))

        correct_operators_x = ((0, 'Z'), (1, 'Z'), (2, 'X'))
        correct_operators_y = ((0, 'Z'), (1, 'Z'), (2, 'Y'))
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, 0.5j)

        self.assertEqual(lowering.terms[correct_operators_x], 0.5)
        self.assertEqual(lowering.terms[correct_operators_y], 0.5j)
        self.assertTrue(lowering.isclose(qtermx + qtermy))

    def test_transm_lower1(self):
        lowering = jordan_wigner(FermionOperator(((1, 0),)))

        correct_operators_x = ((0, 'Z'), (1, 'X'))
        correct_operators_y = ((0, 'Z'), (1, 'Y'))
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, 0.5j)

        self.assertEqual(lowering.terms[correct_operators_x], 0.5)
        self.assertEqual(lowering.terms[correct_operators_y], 0.5j)
        self.assertTrue(lowering.isclose(qtermx + qtermy))

    def test_transm_lower0(self):
        lowering = jordan_wigner(FermionOperator(((0, 0),)))

        correct_operators_x = ((0, 'X'),)
        correct_operators_y = ((0, 'Y'),)
        qtermx = QubitOperator(correct_operators_x, 0.5)
        qtermy = QubitOperator(correct_operators_y, 0.5j)

        self.assertEqual(lowering.terms[correct_operators_x], 0.5)
        self.assertEqual(lowering.terms[correct_operators_y], 0.5j)
        self.assertTrue(lowering.isclose(qtermx + qtermy))

    def test_transm_raise3lower0(self):
        # recall that creation gets -1j on Y and annihilation gets +1j on Y.
        term = jordan_wigner(FermionOperator(((3, 1), (0, 0))))
        self.assertEqual(term.terms[((0, 'X'), (1, 'Z'), (2, 'Z'), (3, 'Y'))],
                         0.25 * 1 * -1j)
        self.assertEqual(term.terms[((0, 'Y'), (1, 'Z'), (2, 'Z'), (3, 'Y'))],
                         0.25 * 1j * -1j)
        self.assertEqual(term.terms[((0, 'Y'), (1, 'Z'), (2, 'Z'), (3, 'X'))],
                         0.25 * 1j * 1)
        self.assertEqual(term.terms[((0, 'X'), (1, 'Z'), (2, 'Z'), (3, 'X'))],
                         0.25 * 1 * 1)

    def test_transm_number(self):
        n = number_operator(self.n_qubits, 3)
        n_jw = jordan_wigner(n)
        self.assertEqual(n_jw.terms[((3, 'Z'),)], -0.5)
        self.assertEqual(n_jw.terms[()], 0.5)
        self.assertEqual(len(n_jw.terms), 2)

    def test_ccr_offsite_even_ca(self):
        c2 = FermionOperator(((2, 1),))
        a4 = FermionOperator(((4, 0),))

        self.assertTrue(normal_ordered(c2 * a4).isclose(
            normal_ordered(-a4 * c2)))
        self.assertTrue(jordan_wigner(c2 * a4).isclose(
            jordan_wigner(-a4 * c2)))

    def test_ccr_offsite_odd_ca(self):
        c1 = FermionOperator(((1, 1),))
        a4 = FermionOperator(((4, 0),))
        self.assertTrue(normal_ordered(c1 * a4).isclose(
            normal_ordered(-a4 * c1)))

        self.assertTrue(jordan_wigner(c1 * a4).isclose(
            jordan_wigner(-a4 * c1)))

    def test_ccr_offsite_even_cc(self):
        c2 = FermionOperator(((2, 1),))
        c4 = FermionOperator(((4, 1),))
        self.assertTrue(normal_ordered(c2 * c4).isclose(
            normal_ordered(-c4 * c2)))

        self.assertTrue(jordan_wigner(c2 * c4).isclose(
            jordan_wigner(-c4 * c2)))

    def test_ccr_offsite_odd_cc(self):
        c1 = FermionOperator(((1, 1),))
        c4 = FermionOperator(((4, 1),))
        self.assertTrue(normal_ordered(c1 * c4).isclose(
            normal_ordered(-c4 * c1)))

        self.assertTrue(jordan_wigner(c1 * c4).isclose(
            jordan_wigner(-c4 * c1)))

    def test_ccr_offsite_even_aa(self):
        a2 = FermionOperator(((2, 0),))
        a4 = FermionOperator(((4, 0),))
        self.assertTrue(normal_ordered(a2 * a4).isclose(
            normal_ordered(-a4 * a2)))

        self.assertTrue(jordan_wigner(a2 * a4).isclose(
            jordan_wigner(-a4 * a2)))

    def test_ccr_offsite_odd_aa(self):
        a1 = FermionOperator(((1, 0),))
        a4 = FermionOperator(((4, 0),))
        self.assertTrue(normal_ordered(a1 * a4).isclose(
            normal_ordered(-a4 * a1)))

        self.assertTrue(jordan_wigner(a1 * a4).isclose(
            jordan_wigner(-a4 * a1)))

    def test_ccr_onsite(self):
        c1 = FermionOperator(((1, 1),))
        a1 = hermitian_conjugated(c1)
        self.assertTrue(normal_ordered(c1 * a1).isclose(
            FermionOperator(()) - normal_ordered(a1 * c1)))
        self.assertTrue(jordan_wigner(c1 * a1).isclose(
            QubitOperator(()) - jordan_wigner(a1 * c1)))

    def test_jordan_wigner_transm_op(self):
        n = number_operator(self.n_qubits)
        n_jw = jordan_wigner(n)
        self.assertEqual(self.n_qubits + 1, len(n_jw.terms))
        self.assertEqual(self.n_qubits / 2., n_jw.terms[()])
        for qubit in range(self.n_qubits):
            operators = ((qubit, 'Z'),)
            self.assertEqual(n_jw.terms[operators], -0.5)


class InteractionOperatorsJWTest(unittest.TestCase):

    def setUp(self):
        self.n_qubits = 5
        self.constant = 0.
        self.one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        self.two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                     self.n_qubits, self.n_qubits), float)
        self.interaction_operator = InteractionOperator(self.constant,
                                                        self.one_body,
                                                        self.two_body)

    def test_jordan_wigner_one_body(self):
        # Make sure it agrees with jordan_wigner(FermionTerm).
        for p in range(self.n_qubits):
            for q in range(self.n_qubits):
                # Get test qubit operator.
                test_operator = jordan_wigner_one_body(p, q)

                # Get correct qubit operator.
                fermion_term = FermionOperator(((p, 1), (q, 0)))
                correct_op = jordan_wigner(fermion_term)
                hermitian_conjugate = hermitian_conjugated(fermion_term)
                if not fermion_term.isclose(hermitian_conjugate):
                    correct_op += jordan_wigner(hermitian_conjugate)

                self.assertTrue(test_operator.isclose(correct_op))

    def test_jordan_wigner_two_body(self):
        # Make sure it agrees with jordan_wigner(FermionTerm).
        for p in range(self.n_qubits):
            for q in range(self.n_qubits):
                for r in range(self.n_qubits):
                    for s in range(self.n_qubits):
                        # Get test qubit operator.
                        test_operator = jordan_wigner_two_body(p, q, r, s)

                        # Get correct qubit operator.
                        fermion_term = FermionOperator(((p, 1), (q, 1),
                                                        (r, 0), (s, 0)))
                        correct_op = jordan_wigner(fermion_term)
                        hermitian_conjugate = hermitian_conjugated(
                            fermion_term)
                        if not fermion_term.isclose(hermitian_conjugate):
                            if p == r and q == s:
                                pass
                            else:
                                correct_op += jordan_wigner(
                                    hermitian_conjugate)

                        self.assertTrue(test_operator.isclose(correct_op),
                                        str(test_operator - correct_op))

    def test_jordan_wigner_twobody_interaction_op_allunique(self):
        test_op = FermionOperator('1^ 2^ 3 4')
        test_op += hermitian_conjugated(test_op)

        retransformed_test_op = reverse_jordan_wigner(jordan_wigner(
            get_interaction_operator(test_op)))

        self.assertTrue(normal_ordered(retransformed_test_op).isclose(
            normal_ordered(test_op)))

    def test_jordan_wigner_twobody_interaction_op_reversal_symmetric(self):
        test_op = FermionOperator('1^ 2^ 2 1')
        test_op += hermitian_conjugated(test_op)
        self.assertTrue(jordan_wigner(test_op).isclose(
                        jordan_wigner(get_interaction_operator(test_op))))

    def test_jordan_wigner_interaction_op_too_few_n_qubits(self):
        with self.assertRaises(ValueError):
            jordan_wigner_interaction_op(self.interaction_operator,
                                         self.n_qubits - 2)

    def test_jordan_wigner_interaction_op_with_zero_term(self):
        test_op = FermionOperator('1^ 2^ 3 4')
        test_op += hermitian_conjugated(test_op)

        interaction_op = get_interaction_operator(test_op)
        interaction_op.constant = 0.0

        retransformed_test_op = reverse_jordan_wigner(jordan_wigner(
            interaction_op))


class GetInteractionOperatorTest(unittest.TestCase):

    def setUp(self):
        self.n_qubits = 5
        self.constant = 0.
        self.one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        self.two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                     self.n_qubits, self.n_qubits), float)

    def test_get_interaction_operator_identity(self):
        interaction_operator = InteractionOperator(-2j, self.one_body,
                                                   self.two_body)
        qubit_operator = jordan_wigner(interaction_operator)
        self.assertTrue(qubit_operator.isclose(-2j * QubitOperator(())))
        self.assertEqual(interaction_operator,
                         get_interaction_operator(reverse_jordan_wigner(
                             qubit_operator), self.n_qubits))

    def test_get_interaction_operator_one_body(self):
        interaction_operator = get_interaction_operator(
            FermionOperator('2^ 2'), self.n_qubits)
        one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        one_body[2, 2] = 1.
        self.assertEqual(interaction_operator,
                         InteractionOperator(0.0, one_body, self.two_body))

    def test_get_interaction_operator_one_body_twoterm(self):
        interaction_operator = get_interaction_operator(
            FermionOperator('2^ 3', -2j) + FermionOperator('3^ 2', 3j),
            self.n_qubits)
        one_body = numpy.zeros((self.n_qubits, self.n_qubits), complex)
        one_body[2, 3] = -2j
        one_body[3, 2] = 3j
        self.assertEqual(interaction_operator,
                         InteractionOperator(0.0, one_body, self.two_body))

    def test_get_interaction_operator_two_body(self):
        interaction_operator = get_interaction_operator(
            FermionOperator('2^ 2 3^ 4'), self.n_qubits)
        two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                self.n_qubits, self.n_qubits), float)
        two_body[3, 2, 4, 2] = -1.
        self.assertEqual(interaction_operator,
                         InteractionOperator(0.0, self.one_body, two_body))

    def test_get_interaction_operator_two_body_distinct(self):
        interaction_operator = get_interaction_operator(
            FermionOperator('0^ 1^ 2 3'), self.n_qubits)
        two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                self.n_qubits, self.n_qubits), float)
        two_body[1, 0, 3, 2] = 1.
        self.assertEqual(interaction_operator,
                         InteractionOperator(0.0, self.one_body, two_body))