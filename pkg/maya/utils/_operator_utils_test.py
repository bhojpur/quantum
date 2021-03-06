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

"""Tests for operator_utils."""
from __future__ import absolute_import

import numpy
import os
import unittest

from maya.config import *
from maya.ops import *
from maya.transforms import jordan_wigner, get_interaction_operator
from maya.utils import (eigenspectrum, commutator,
                            count_qubits, is_identity)
from maya.utils._operator_utils import (commutator, count_qubits,
                                            eigenspectrum, get_file_path,
                                            is_identity, load_operator,
                                            OperatorUtilsError, save_operator)

from divya.ops import QubitOperator

class OperatorUtilsTest(unittest.TestCase):

    def setUp(self):
        self.n_qubits = 5
        self.fermion_term = FermionOperator('1^ 2^ 3 4', -3.17)
        self.fermion_operator = self.fermion_term + hermitian_conjugated(
            self.fermion_term)
        self.qubit_operator = jordan_wigner(self.fermion_operator)
        self.interaction_operator = get_interaction_operator(
            self.fermion_operator)

    def test_n_qubits_single_fermion_term(self):
        self.assertEqual(self.n_qubits,
                         count_qubits(self.fermion_term))

    def test_n_qubits_fermion_operator(self):
        self.assertEqual(self.n_qubits,
                         count_qubits(self.fermion_operator))

    def test_n_qubits_qubit_operator(self):
        self.assertEqual(self.n_qubits,
                         count_qubits(self.qubit_operator))

    def test_n_qubits_interaction_operator(self):
        self.assertEqual(self.n_qubits,
                         count_qubits(self.interaction_operator))

    def test_n_qubits_bad_type(self):
        with self.assertRaises(TypeError):
            count_qubits('twelve')

    def test_eigenspectrum(self):
        fermion_eigenspectrum = eigenspectrum(self.fermion_operator)
        qubit_eigenspectrum = eigenspectrum(self.qubit_operator)
        interaction_eigenspectrum = eigenspectrum(self.interaction_operator)
        for i in range(2 ** self.n_qubits):
            self.assertAlmostEqual(fermion_eigenspectrum[i],
                                   qubit_eigenspectrum[i])
            self.assertAlmostEqual(fermion_eigenspectrum[i],
                                   interaction_eigenspectrum[i])

    def test_is_identity_unit_fermionoperator(self):
        self.assertTrue(is_identity(FermionOperator(())))

    def test_is_identity_double_of_unit_fermionoperator(self):
        self.assertTrue(is_identity(2. * FermionOperator(())))

    def test_is_identity_unit_qubitoperator(self):
        self.assertTrue(is_identity(QubitOperator(())))

    def test_is_identity_double_of_unit_qubitoperator(self):
        self.assertTrue(is_identity(QubitOperator((), 2.)))

    def test_not_is_identity_single_term_fermionoperator(self):
        self.assertFalse(is_identity(FermionOperator('1^')))

    def test_not_is_identity_single_term_qubitoperator(self):
        self.assertFalse(is_identity(QubitOperator('X1')))

    def test_not_is_identity_zero_fermionoperator(self):
        self.assertFalse(is_identity(FermionOperator()))

    def test_not_is_identity_zero_qubitoperator(self):
        self.assertFalse(is_identity(QubitOperator()))

    def test_is_identity_bad_type(self):
        with self.assertRaises(TypeError):
            is_identity('eleven')


class SaveLoadOperatorTest(unittest.TestCase):
    def setUp(self):
        self.n_qubits = 5
        self.fermion_term = FermionOperator('1^ 2^ 3 4', -3.17)
        self.fermion_operator = self.fermion_term + hermitian_conjugated(
            self.fermion_term)
        self.qubit_operator = jordan_wigner(self.fermion_operator)
        self.file_name = "test_file"

    def tearDown(self):
        file_path = os.path.join(DATA_DIRECTORY, self.file_name + '.data')
        if os.path.isfile(file_path):
            os.remove(file_path)

    def test_save_and_load_fermion_operators(self):
        save_operator(self.fermion_operator, self.file_name)
        loaded_fermion_operator = load_operator(self.file_name)
        self.assertEqual(self.fermion_operator.terms,
                         loaded_fermion_operator.terms,
                         msg=str(self.fermion_operator -
                                 loaded_fermion_operator))

    def test_save_and_load_qubit_operators(self):
        save_operator(self.qubit_operator, self.file_name)
        loaded_qubit_operator = load_operator(self.file_name)
        self.assertEqual(self.qubit_operator.terms,
                         loaded_qubit_operator.terms)

    def test_save_no_filename_operator_utils_error(self):
        with self.assertRaises(OperatorUtilsError):
            save_operator(self.fermion_operator)

    def test_basic_save(self):
        save_operator(self.fermion_operator, self.file_name)

    def test_save_interaction_operator_not_implemented(self):
        constant = 100.0
        one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                self.n_qubits, self.n_qubits), float)
        one_body[1, 1] = 10.0
        two_body[1, 2, 3, 4] = 12.0
        interaction_operator = InteractionOperator(
            constant, one_body, two_body)
        with self.assertRaises(NotImplementedError):
            save_operator(interaction_operator, self.file_name)

    def test_save_on_top_of_existing_operator_utils_error(self):
        save_operator(self.fermion_operator, self.file_name)
        with self.assertRaises(OperatorUtilsError):
            save_operator(self.fermion_operator, self.file_name)

    def test_load_bad_type(self):
        with self.assertRaises(TypeError):
            load_operator('bad_type_operator')

    def test_save_bad_type(self):
        with self.assertRaises(TypeError):
            save_operator('ping', 'somewhere')


class CommutatorTest(unittest.TestCase):

    def setUp(self):
        self.fermion_term = FermionOperator('1^ 2^ 3 4', -3.17)
        self.fermion_operator = self.fermion_term + hermitian_conjugated(
            self.fermion_term)
        self.qubit_operator = jordan_wigner(self.fermion_operator)

    def test_commutes_identity(self):
        com = commutator(FermionOperator.identity(),
                         FermionOperator('2^ 3', 2.3))
        self.assertTrue(com.isclose(FermionOperator.zero()))

    def test_commutes_no_intersection(self):
        com = commutator(FermionOperator('2^ 3'), FermionOperator('4^ 5^ 3'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(FermionOperator.zero()))

    def test_commutes_number_operators(self):
        com = commutator(FermionOperator('4^ 3^ 4 3'), FermionOperator('2^ 2'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(FermionOperator.zero()))

    def test_commutator_hopping_operators(self):
        com = commutator(3 * FermionOperator('1^ 2'), FermionOperator('2^ 3'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(FermionOperator('1^ 3', 3)))

    def test_commutator_hopping_with_single_number(self):
        com = commutator(FermionOperator('1^ 2', 1j), FermionOperator('1^ 1'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(-FermionOperator('1^ 2') * 1j))

    def test_commutator_hopping_with_double_number_one_intersection(self):
        com = commutator(FermionOperator('1^ 3'), FermionOperator('3^ 2^ 3 2'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(-FermionOperator('2^ 1^ 3 2')))

    def test_commutator_hopping_with_double_number_two_intersections(self):
        com = commutator(FermionOperator('2^ 3'), FermionOperator('3^ 2^ 3 2'))
        com = normal_ordered(com)
        self.assertTrue(com.isclose(FermionOperator.zero()))

    def test_commutator(self):
        operator_a = FermionOperator('')
        self.assertTrue(FermionOperator().isclose(
            commutator(operator_a, self.fermion_operator)))
        operator_b = QubitOperator('X1 Y2')
        self.assertTrue(commutator(self.qubit_operator, operator_b).isclose(
            self.qubit_operator * operator_b -
            operator_b * self.qubit_operator))

    def test_commutator_operator_a_bad_type(self):
        with self.assertRaises(TypeError):
            commutator(1, self.fermion_operator)

    def test_commutator_operator_b_bad_type(self):
        with self.assertRaises(TypeError):
            commutator(self.qubit_operator, "hello")

    def test_commutator_not_same_type(self):
        with self.assertRaises(TypeError):
            commutator(self.fermion_operator, self.qubit_operator)