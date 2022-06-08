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

"""Tests for _jellium_hf_state.py."""
from __future__ import absolute_import

from itertools import permutations
from scipy.sparse import csr_matrix

import numpy
import unittest

from maya.transforms import get_sparse_operator
from maya.utils import expectation, get_ground_state, Grid, jellium_model
from maya.utils._plane_wave_hamiltonian import wigner_seitz_length_scale
from maya.utils._sparse_tools import jw_number_restrict_operator

from maya.utils._jellium_hf_state import hartree_fock_state_jellium

class JelliumHartreeFockStateTest(unittest.TestCase):
    def test_hf_state_energy_close_to_ground_energy_at_high_density(self):
        grid_length = 8
        dimension = 1
        spinless = True
        n_particles = grid_length ** dimension // 2

        # High density -> small length_scale.
        length_scale = 0.25

        grid = Grid(dimension, grid_length, length_scale)
        hamiltonian = jellium_model(grid, spinless)
        hamiltonian_sparse = get_sparse_operator(hamiltonian)

        hf_state = hartree_fock_state_jellium(grid, n_particles,
                                              spinless, plane_wave=True)

        restricted_hamiltonian = jw_number_restrict_operator(
            hamiltonian_sparse, n_particles)

        E_g = get_ground_state(restricted_hamiltonian)[0]
        E_HF_plane_wave = expectation(hamiltonian_sparse, hf_state)

        self.assertAlmostEqual(E_g, E_HF_plane_wave, places=5)

    def test_hf_state_energy_same_in_plane_wave_and_dual_basis(self):
        grid_length = 4
        dimension = 1
        wigner_seitz_radius = 10.0
        spinless = False

        n_orbitals = grid_length ** dimension
        if not spinless:
            n_orbitals *= 2
        n_particles = n_orbitals // 2

        length_scale = wigner_seitz_length_scale(
            wigner_seitz_radius, n_particles, dimension)

        grid = Grid(dimension, grid_length, length_scale)
        hamiltonian = jellium_model(grid, spinless)
        hamiltonian_dual_basis = jellium_model(
            grid, spinless, plane_wave=False)

        # Get the Hamiltonians as sparse operators.
        hamiltonian_sparse = get_sparse_operator(hamiltonian)
        hamiltonian_dual_sparse = get_sparse_operator(hamiltonian_dual_basis)

        hf_state = hartree_fock_state_jellium(
            grid, n_particles, spinless, plane_wave=True)
        hf_state_dual = hartree_fock_state_jellium(
            grid, n_particles, spinless, plane_wave=False)

        E_HF_plane_wave = expectation(hamiltonian_sparse, hf_state)
        E_HF_dual = expectation(hamiltonian_dual_sparse, hf_state_dual)

        self.assertAlmostEqual(E_HF_dual, E_HF_plane_wave)

    def test_hf_state_plane_wave_basis_lowest_single_determinant_state(self):
        grid_length = 7
        dimension = 1
        spinless = True
        n_particles = 4
        length_scale = 2.0

        grid = Grid(dimension, grid_length, length_scale)
        hamiltonian = jellium_model(grid, spinless)
        hamiltonian_sparse = get_sparse_operator(hamiltonian)

        hf_state = hartree_fock_state_jellium(grid, n_particles,
                                              spinless, plane_wave=True)

        HF_energy = expectation(hamiltonian_sparse, hf_state)

        for occupied_orbitals in permutations(
                [1] * n_particles + [0] * (grid_length - n_particles)):
            state_index = numpy.sum(2 ** numpy.array(occupied_orbitals))
            HF_competitor = csr_matrix(([1.0], ([state_index], [0])),
                                       shape=(2 ** grid_length, 1))

            self.assertLessEqual(
                HF_energy, expectation(hamiltonian_sparse, HF_competitor))