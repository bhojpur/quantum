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

"""Tests for Hubbard model module."""
from __future__ import absolute_import

import unittest

from maya.utils import fermi_hubbard

class FermiHubbardTest(unittest.TestCase):

    def setUp(self):
        self.x_dimension = 2
        self.y_dimension = 2
        self.tunneling = 2.
        self.coulomb = 1.
        self.magnetic_field = 0.5
        self.chemical_potential = 0.25
        self.periodic = 0
        self.spinless = 0

    def test_two_by_two_spinful(self):

        # Initialize the Hamiltonian.
        hubbard_model = fermi_hubbard(
            self.x_dimension, self.y_dimension, self.tunneling, self.coulomb,
            self.chemical_potential, self.magnetic_field,
            self.periodic, self.spinless)

        # Check up spin on site terms.
        self.assertAlmostEqual(hubbard_model.terms[((0, 1), (0, 0))], -.75)
        self.assertAlmostEqual(hubbard_model.terms[((2, 1), (2, 0))], -.75)
        self.assertAlmostEqual(hubbard_model.terms[((4, 1), (4, 0))], -.75)
        self.assertAlmostEqual(hubbard_model.terms[((6, 1), (6, 0))], -.75)

        # Check down spin on site terms.
        self.assertAlmostEqual(hubbard_model.terms[((1, 1), (1, 0))], .25)
        self.assertAlmostEqual(hubbard_model.terms[((3, 1), (3, 0))], .25)
        self.assertAlmostEqual(hubbard_model.terms[((5, 1), (5, 0))], .25)
        self.assertAlmostEqual(hubbard_model.terms[((7, 1), (7, 0))], .25)

        # Check up right/left hopping terms.
        self.assertAlmostEqual(hubbard_model.terms[((0, 1), (2, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((2, 1), (0, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((4, 1), (6, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((6, 1), (4, 0))], -2.)

        # Check up top/bottom hopping terms.
        self.assertAlmostEqual(hubbard_model.terms[((0, 1), (4, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((4, 1), (0, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((2, 1), (6, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((6, 1), (2, 0))], -2.)

        # Check down right/left hopping terms.
        self.assertAlmostEqual(hubbard_model.terms[((1, 1), (3, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((3, 1), (1, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((5, 1), (7, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((7, 1), (5, 0))], -2.)

        # Check down top/bottom hopping terms.
        self.assertAlmostEqual(hubbard_model.terms[((1, 1), (5, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((5, 1), (1, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((3, 1), (7, 0))], -2.)
        self.assertAlmostEqual(hubbard_model.terms[((7, 1), (3, 0))], -2.)

        # Check on site interaction term.
        self.assertAlmostEqual(hubbard_model.terms[((0, 1), (0, 0),
                                                    (1, 1), (1, 0))], 1.)
        self.assertAlmostEqual(hubbard_model.terms[((2, 1), (2, 0),
                                                    (3, 1), (3, 0))], 1.)
        self.assertAlmostEqual(hubbard_model.terms[((4, 1), (4, 0),
                                                    (5, 1), (5, 0))], 1.)
        self.assertAlmostEqual(hubbard_model.terms[((6, 1), (6, 0),
                                                    (7, 1), (7, 0))], 1.)

    def test_two_by_two_spinful_periodic_rudimentary(self):
        hubbard_model = fermi_hubbard(
            self.x_dimension, self.y_dimension, self.tunneling, self.coulomb,
            self.chemical_potential, self.magnetic_field,
            periodic=True, spinless=False)

    def test_two_by_two_spinful_aperiodic_rudimentary(self):
        hubbard_model = fermi_hubbard(
            self.x_dimension, self.y_dimension, self.tunneling, self.coulomb,
            self.chemical_potential, self.magnetic_field,
            periodic=False, spinless=False)

    def test_two_by_two_spinless_periodic_rudimentary(self):
        hubbard_model = fermi_hubbard(
            self.x_dimension, self.y_dimension, self.tunneling, self.coulomb,
            self.chemical_potential, self.magnetic_field,
            periodic=True, spinless=True)