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

"""Tests  _bravyi_kitaev_fast_test.py."""
from __future__ import absolute_import
import os
import unittest

from maya.config import (THIS_DIRECTORY)
from maya.ops import (FermionOperator, InteractionOperator, normal_ordered)
from maya.transforms._conversion import (get_fermion_operator,
                                             get_sparse_operator)
from maya.transforms._jordan_wigner import (jordan_wigner,
                                                jordan_wigner_one_body)
from maya.utils import (count_qubits, MolecularData, eigenspectrum)

import numpy
from divya.ops import QubitOperator

from . import _bksf


class bravyi_kitaev_fastTransformTest(unittest.TestCase):
    def setUp(self):
        geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.7414))]
        basis = 'sto-3g'
        multiplicity = 1
        filename = os.path.join(THIS_DIRECTORY, 'data',
                                'H2_sto-3g_singlet_0.7414')
        self.molecule = MolecularData(
            geometry, basis, multiplicity, filename=filename)
        self.molecule.load()

        # Get molecular Hamiltonian.
        self.molecular_hamiltonian = self.molecule.get_molecular_hamiltonian()

        # Get FCI RDM.
        self.fci_rdm = self.molecule.get_molecular_rdm(use_fci=1)
        # Get explicit coefficients.
        self.nuclear_repulsion = self.molecular_hamiltonian.constant
        self.one_body = self.molecular_hamiltonian.one_body_tensor
        self.two_body = self.molecular_hamiltonian.two_body_tensor

        # Get fermion Hamiltonian.
        self.fermion_hamiltonian = normal_ordered(get_fermion_operator(
                                                  self.molecular_hamiltonian))

        # Get qubit Hamiltonian.
        self.qubit_hamiltonian = jordan_wigner(self.fermion_hamiltonian)

        # Get the sparse matrix.
        self.hamiltonian_matrix = get_sparse_operator(
                                                    self.molecular_hamiltonian)

    def test_bad_input(self):
        with self.assertRaises(TypeError):
            _bksf.bravyi_kitaev_fast(FermionOperator())

    def test_bravyi_kitaev_fast_edgeoperator_Bi(self):
        # checking the edge operators
        edge_matrix = numpy.triu(numpy.ones((4, 4)))
        edge_matrix_indices = numpy.array(numpy.nonzero(
                                          numpy.triu(edge_matrix) -
                                          numpy.diag(numpy.diag(edge_matrix))))

        correct_operators_b0 = ((0, 'Z'), (1, 'Z'), (2, 'Z'))
        correct_operators_b1 = ((0, 'Z'), (3, 'Z'), (4, 'Z'))
        correct_operators_b2 = ((1, 'Z'), (3, 'Z'), (5, 'Z'))
        correct_operators_b3 = ((2, 'Z'), (4, 'Z'), (5, 'Z'))

        qterm_b0 = QubitOperator(correct_operators_b0, 1)
        qterm_b1 = QubitOperator(correct_operators_b1, 1)
        qterm_b2 = QubitOperator(correct_operators_b2, 1)
        qterm_b3 = QubitOperator(correct_operators_b3, 1)
        self.assertTrue(qterm_b0.isclose(
                        _bksf.edge_operator_b(edge_matrix_indices, 0)))
        self.assertTrue(qterm_b1.isclose(
                        _bksf.edge_operator_b(edge_matrix_indices, 1)))
        self.assertTrue(qterm_b2.isclose(
                        _bksf.edge_operator_b(edge_matrix_indices, 2)))
        self.assertTrue(qterm_b3.isclose(
                        _bksf.edge_operator_b(edge_matrix_indices, 3)))

    def test_bravyi_kitaev_fast_edgeoperator_Aij(self):
        # checking the edge operators
        edge_matrix = numpy.triu(numpy.ones((4, 4)))
        edge_matrix_indices = numpy.array(numpy.nonzero(
                                          numpy.triu(edge_matrix) -
                                          numpy.diag(numpy.diag(edge_matrix))))
        correct_operators_a01 = ((0, 'X'),)
        correct_operators_a02 = ((0, 'Z'), (1, 'X'))
        correct_operators_a03 = ((0, 'Z'), (1, 'Z'), (2, 'X'))
        correct_operators_a12 = ((0, 'Z'), (1, 'Z'), (3, 'X'))
        correct_operators_a13 = ((0, 'Z'), (2, 'Z'), (3, 'Z'), (4, 'X'))
        correct_operators_a23 = ((1, 'Z'), (2, 'Z'), (3, 'Z'),
                                 (4, 'Z'), (5, 'X'))

        qterm_a01 = QubitOperator(correct_operators_a01, 1)
        qterm_a02 = QubitOperator(correct_operators_a02, 1)
        qterm_a03 = QubitOperator(correct_operators_a03, 1)
        qterm_a12 = QubitOperator(correct_operators_a12, 1)
        qterm_a13 = QubitOperator(correct_operators_a13, 1)
        qterm_a23 = QubitOperator(correct_operators_a23, 1)

        self.assertTrue(qterm_a01.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 0, 1)))
        self.assertTrue(qterm_a02.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 0, 2)))
        self.assertTrue(qterm_a03.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 0, 3)))
        self.assertTrue(qterm_a12.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 1, 2)))
        self.assertTrue(qterm_a13.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 1, 3)))
        self.assertTrue(qterm_a23.isclose(_bksf.edge_operator_aij(
                                          edge_matrix_indices, 2, 3)))

    def test_bravyi_kitaev_fast_jw_number_operator(self):
        # bksf algorithm allows for even number of particles. So, compare the
        # spectrum of number operator from jordan-wigner and bksf algorithm
        # to make sure half of the jordan-wigner number operator spectrum
        # can be found in bksf number operator spectrum.
        bravyi_kitaev_fast_n = _bksf.number_operator(
                                                    self.molecular_hamiltonian)
        jw_n = QubitOperator()
        n_qubits = count_qubits(self.molecular_hamiltonian)
        for i in range(n_qubits):
            jw_n += jordan_wigner_one_body(i, i)
        jw_eig_spec = eigenspectrum(jw_n)
        bravyi_kitaev_fast_eig_spec = eigenspectrum(bravyi_kitaev_fast_n)
        evensector = 0
        for i in range(numpy.size(jw_eig_spec)):
            if bool(numpy.size(numpy.where(jw_eig_spec[i] ==
                                           bravyi_kitaev_fast_eig_spec))):
                evensector += 1
        self.assertEqual(evensector, 2**(n_qubits - 1))

    def test_bravyi_kitaev_fast_jw_hamiltonian(self):
        # make sure half of the jordan-wigner Hamiltonian eigenspectrum can
        # be found in bksf Hamiltonian eigenspectrum.
        n_qubits = count_qubits(self.molecular_hamiltonian)
        bravyi_kitaev_fast_H = _bksf.bravyi_kitaev_fast(
                                                    self.molecular_hamiltonian)
        jw_H = jordan_wigner(self.molecular_hamiltonian)
        bravyi_kitaev_fast_H_eig = eigenspectrum(bravyi_kitaev_fast_H)
        jw_H_eig = eigenspectrum(jw_H)
        bravyi_kitaev_fast_H_eig = bravyi_kitaev_fast_H_eig.round(5)
        jw_H_eig = jw_H_eig.round(5)
        evensector = 0
        for i in range(numpy.size(jw_H_eig)):
            if bool(numpy.size(numpy.where(jw_H_eig[i] ==
                                           bravyi_kitaev_fast_H_eig))):
                evensector += 1
        self.assertEqual(evensector, 2**(n_qubits - 1))

    def test_bravyi_kitaev_fast_generate_fermions(self):
        # test for generating two fermions
        edge_matrix = _bksf.bravyi_kitaev_fast_edge_matrix(
                        self.molecular_hamiltonian)
        edge_matrix_indices = numpy.array(numpy.nonzero(
                                numpy.triu(edge_matrix) - numpy.diag(
                                        numpy.diag(edge_matrix))))
        fermion_generation_operator = _bksf.generate_fermions(
                                      edge_matrix_indices, 2, 3)
        fermion_generation_sp_matrix = get_sparse_operator(
                                        fermion_generation_operator)
        fermion_generation_matrix = fermion_generation_sp_matrix.toarray()
        bksf_vacuum_state_operator = _bksf.vacuum_operator(edge_matrix_indices)
        bksf_vacuum_state_sp_matrix = get_sparse_operator(
                                      bksf_vacuum_state_operator)
        bksf_vacuum_state_matrix = bksf_vacuum_state_sp_matrix.toarray()
        vacuum_state = numpy.zeros((64, 1))
        vacuum_state[0] = 1.
        bksf_vacuum_state = numpy.dot(bksf_vacuum_state_matrix, vacuum_state)
        two_fermion_state = numpy.dot(fermion_generation_matrix,
                                      bksf_vacuum_state)
        # using total number operator to check the number of fermions generated
        tot_number_operator = _bksf.number_operator(self.molecular_hamiltonian)
        number_operator_sp_matrix = get_sparse_operator(tot_number_operator)
        number_operator_matrix = number_operator_sp_matrix.toarray()
        tot_fermions = numpy.dot(two_fermion_state.conjugate().T,
                                 numpy.dot(number_operator_matrix,
                                 two_fermion_state))
        # checking the occupation number of site 2 and 3
        number_operator_2 = _bksf.number_operator(self.molecular_hamiltonian,
                                                  2)
        number_operator_3 = _bksf.number_operator(self.molecular_hamiltonian,
                                                  3)
        number_operator_23 = number_operator_2 + number_operator_3
        number_operator_23_sp_matrix = get_sparse_operator(number_operator_23)
        number_operator_23_matrix = number_operator_23_sp_matrix.toarray()
        tot_23_fermions = numpy.dot(two_fermion_state.conjugate().T,
                                    numpy.dot(number_operator_23_matrix,
                                              two_fermion_state))
        self.assertTrue(2.0 - float(tot_fermions.real) < 1e-13)
        self.assertTrue(2.0 - float(tot_23_fermions.real) < 1e-13)

    def test_bravyi_kitaev_fast_excitation_terms(self):
        # Testing on-site and excitation terms in Hamiltonian
        constant = 0
        one_body = numpy.array([[1, 2, 0, 3], [2, 1, 2, 0], [0, 2, 1, 2.5],
                                [3, 0, 2.5, 1]])
        # No Coloumb interaction
        two_body = numpy.zeros((4, 4, 4, 4))
        molecular_hamiltonian = InteractionOperator(constant,
                                                    one_body, two_body)
        n_qubits = count_qubits(molecular_hamiltonian)
        # comparing the eigenspectrum of Hamiltonian
        bravyi_kitaev_fast_H = _bksf.bravyi_kitaev_fast(molecular_hamiltonian)
        jw_H = jordan_wigner(molecular_hamiltonian)
        bravyi_kitaev_fast_H_eig = eigenspectrum(bravyi_kitaev_fast_H)
        jw_H_eig = eigenspectrum(jw_H)
        bravyi_kitaev_fast_H_eig = bravyi_kitaev_fast_H_eig.round(5)
        jw_H_eig = jw_H_eig.round(5)
        evensector_H = 0
        for i in range(numpy.size(jw_H_eig)):
            if bool(numpy.size(numpy.where(jw_H_eig[i] ==
                                           bravyi_kitaev_fast_H_eig))):
                evensector_H += 1

        # comparing eigenspectrum of number operator
        bravyi_kitaev_fast_n = _bksf.number_operator(molecular_hamiltonian)
        jw_n = QubitOperator()
        n_qubits = count_qubits(molecular_hamiltonian)
        for i in range(n_qubits):
            jw_n += jordan_wigner_one_body(i, i)
        jw_eig_spec = eigenspectrum(jw_n)
        bravyi_kitaev_fast_eig_spec = eigenspectrum(bravyi_kitaev_fast_n)
        evensector_n = 0
        for i in range(numpy.size(jw_eig_spec)):
            if bool(numpy.size(numpy.where(jw_eig_spec[i] ==
                                           bravyi_kitaev_fast_eig_spec))):
                evensector_n += 1
        self.assertEqual(evensector_H, 2**(n_qubits - 1))
        self.assertEqual(evensector_n, 2**(n_qubits - 1))

    def test_bravyi_kitaev_fast_number_excitation_operator(self):
        # using hydrogen Hamiltonian and introducing some number operator terms
        constant = 0
        one_body = numpy.zeros((4, 4))
        one_body[(0, 0)] = .4
        one_body[(1, 1)] = .5
        one_body[(2, 2)] = .6
        one_body[(3, 3)] = .7
        two_body = self.molecular_hamiltonian.two_body_tensor
        # initiating number operator terms for all the possible cases
        two_body[(1, 2, 3, 1)] = 0.1
        two_body[(1, 3, 2, 1)] = 0.1
        two_body[(1, 2, 1, 3)] = 0.15
        two_body[(3, 1, 2, 1)] = 0.15
        two_body[(0, 2, 2, 1)] = 0.09
        two_body[(1, 2, 2, 0)] = 0.09
        two_body[(1, 2, 3, 2)] = 0.11
        two_body[(2, 3, 2, 1)] = 0.11
        two_body[(2, 2, 2, 2)] = 0.1
        molecular_hamiltonian = InteractionOperator(constant,
                                                    one_body, two_body)
        # comparing the eigenspectrum of Hamiltonian
        n_qubits = count_qubits(molecular_hamiltonian)
        bravyi_kitaev_fast_H = _bksf.bravyi_kitaev_fast(molecular_hamiltonian)
        jw_H = jordan_wigner(molecular_hamiltonian)
        bravyi_kitaev_fast_H_eig = eigenspectrum(bravyi_kitaev_fast_H)
        jw_H_eig = eigenspectrum(jw_H)
        bravyi_kitaev_fast_H_eig = bravyi_kitaev_fast_H_eig.round(5)
        jw_H_eig = jw_H_eig.round(5)
        evensector_H = 0
        for i in range(numpy.size(jw_H_eig)):
            if bool(numpy.size(numpy.where(jw_H_eig[i] ==
                                           bravyi_kitaev_fast_H_eig))):
                evensector_H += 1

        # comparing eigenspectrum of number operator
        bravyi_kitaev_fast_n = _bksf.number_operator(molecular_hamiltonian)
        jw_n = QubitOperator()
        n_qubits = count_qubits(molecular_hamiltonian)
        for i in range(n_qubits):
            jw_n += jordan_wigner_one_body(i, i)
        jw_eig_spec = eigenspectrum(jw_n)
        bravyi_kitaev_fast_eig_spec = eigenspectrum(bravyi_kitaev_fast_n)
        evensector_n = 0
        for i in range(numpy.size(jw_eig_spec)):
            if bool(numpy.size(numpy.where(jw_eig_spec[i] ==
                                           bravyi_kitaev_fast_eig_spec))):
                evensector_n += 1
        self.assertEqual(evensector_H, 2**(n_qubits - 1))
        self.assertEqual(evensector_n, 2**(n_qubits - 1))

if __name__ == '__main__':
    unittest.main()