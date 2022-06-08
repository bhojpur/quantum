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

"""Tests for chemical_series."""
from __future__ import absolute_import

import numpy
import os
import unittest

from maya.utils import (make_atom,
                            make_atomic_lattice,
                            make_atomic_ring,
                            periodic_table)
from maya.utils._chemical_series import MolecularLatticeError
from maya.utils._molecular_data import periodic_polarization


class ChemicalSeries(unittest.TestCase):

    def test_make_atomic_ring(self):
        spacing = 1.
        basis = 'sto-3g'
        for n_atoms in range(2, 10):
            molecule = make_atomic_ring(n_atoms, spacing, basis)

            # Check that ring is centered.
            vector_that_should_sum_to_zero = 0.
            for atom in molecule.geometry:
                for coordinate in atom[1]:
                    vector_that_should_sum_to_zero += coordinate
            self.assertAlmostEqual(vector_that_should_sum_to_zero, 0.)

            # Check that the spacing between the atoms is correct.
            for atom_index in range(n_atoms):
                if atom_index:
                    atom_b = molecule.geometry[atom_index]
                    coords_b = atom_b[1]
                    atom_a = molecule.geometry[atom_index - 1]
                    coords_a = atom_a[1]
                    observed_spacing = numpy.sqrt(numpy.square(
                        coords_b[0] - coords_a[0]) + numpy.square(
                        coords_b[1] - coords_a[1]) + numpy.square(
                        coords_b[2] - coords_a[2]))
                    self.assertAlmostEqual(observed_spacing, spacing)

    def test_make_atomic_lattice_1d(self):
        spacing = 1.7
        basis = 'sto-3g'
        atom_type = 'H'
        for n_atoms in range(2, 10):
            molecule = make_atomic_lattice(n_atoms, 1, 1,
                                           spacing, basis, atom_type)

            # Check that the spacing between the atoms is correct.
            for atom_index in range(n_atoms):
                if atom_index:
                    atom_b = molecule.geometry[atom_index]
                    coords_b = atom_b[1]
                    atom_a = molecule.geometry[atom_index - 1]
                    coords_a = atom_a[1]
                    self.assertAlmostEqual(coords_b[0] - coords_a[0], spacing)
                    self.assertAlmostEqual(coords_b[1] - coords_a[1], 0)
                    self.assertAlmostEqual(coords_b[2] - coords_a[2], 0)

    def test_make_atomic_lattice_2d(self):
        spacing = 1.7
        basis = 'sto-3g'
        atom_type = 'H'
        atom_dim = 7
        molecule = make_atomic_lattice(atom_dim, atom_dim, 1,
                                       spacing, basis, atom_type)

        # Check that the spacing between the atoms is correct.
        for atom in range(atom_dim ** 2):
            coords = molecule.geometry[atom][1]

            # Check y-coord.
            grid_y = atom % atom_dim
            self.assertAlmostEqual(coords[1], spacing * grid_y)

            # Check x-coord.
            grid_x = atom // atom_dim
            self.assertAlmostEqual(coords[0], spacing * grid_x)

    def test_make_atomic_lattice_3d(self):
        spacing = 1.7
        basis = 'sto-3g'
        atom_type = 'H'
        atom_dim = 4
        molecule = make_atomic_lattice(atom_dim, atom_dim, atom_dim,
                                       spacing, basis, atom_type)

        # Check that the spacing between the atoms is correct.
        for atom in range(atom_dim ** 3):
            coords = molecule.geometry[atom][1]

            # Check z-coord.
            grid_z = atom % atom_dim
            self.assertAlmostEqual(coords[2], spacing * grid_z)

            # Check y-coord.
            grid_y = (atom // atom_dim) % atom_dim
            self.assertAlmostEqual(coords[1], spacing * grid_y)

            # Check x-coord.
            grid_x = atom // atom_dim ** 2
            self.assertAlmostEqual(coords[0], spacing * grid_x)

    def test_make_atomic_lattice_0d_raise_error(self):
        spacing = 1.7
        basis = 'sto-3g'
        atom_type = 'H'
        atom_dim = 0
        with self.assertRaises(MolecularLatticeError):
            make_atomic_lattice(atom_dim, atom_dim, atom_dim,
                                spacing, basis, atom_type)

    def test_make_atom(self):
        basis = 'sto-3g'
        largest_atom = 30
        for n_electrons in range(1, largest_atom):
            atom_name = periodic_table[n_electrons]
            atom = make_atom(atom_name, basis)
            expected_spin = periodic_polarization[n_electrons] / 2.
            expected_multiplicity = int(2 * expected_spin + 1)
            self.assertAlmostEqual(expected_multiplicity, atom.multiplicity)