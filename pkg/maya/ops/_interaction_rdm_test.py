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

"""Tests for interaction_rdms.py."""
from __future__ import absolute_import

import unittest

from maya.config import *
from maya.ops._interaction_rdm import InteractionRDMError
from maya.transforms import jordan_wigner
from maya.utils import MolecularData

from divya.ops import QubitOperator

class InteractionRDMTest(unittest.TestCase):

    def setUp(self):
        geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.7414))]
        basis = 'sto-3g'
        multiplicity = 1
        filename = os.path.join(THIS_DIRECTORY, 'data',
                                'H2_sto-3g_singlet_0.7414')
        self.molecule = MolecularData(
            geometry, basis, multiplicity, filename=filename)
        self.molecule.load()
        self.cisd_energy = self.molecule.cisd_energy
        self.rdm = self.molecule.get_molecular_rdm()
        self.hamiltonian = self.molecule.get_molecular_hamiltonian()

    def test_get_qubit_expectations(self):
        qubit_operator = jordan_wigner(self.hamiltonian)
        qubit_expectations = self.rdm.get_qubit_expectations(qubit_operator)

        test_energy = 0.0
        for qubit_term in qubit_expectations.terms:
            term_coefficient = qubit_operator.terms[qubit_term]
            test_energy += (term_coefficient *
                            qubit_expectations.terms[qubit_term])
        self.assertLess(abs(test_energy - self.cisd_energy), EQ_TOLERANCE)

    def test_get_qubit_expectations_nonmolecular_term(self):
        with self.assertRaises(InteractionRDMError):
            self.rdm.get_qubit_expectations(QubitOperator('X1 X2 X3 X4 Y6'))

    def test_get_qubit_expectations_through_expectation_method(self):
        qubit_operator = jordan_wigner(self.hamiltonian)
        test_energy = self.rdm.expectation(qubit_operator)

        self.assertLess(abs(test_energy - self.cisd_energy), EQ_TOLERANCE)

    def test_get_molecular_operator_expectation(self):
        expectation = self.rdm.expectation(self.hamiltonian)
        self.assertAlmostEqual(expectation, self.cisd_energy, places=7)

    def test_expectation_bad_type(self):
        with self.assertRaises(InteractionRDMError):
            self.rdm.expectation(12)