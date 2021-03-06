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

from __future__ import absolute_import

import unittest

import numpy

from maya.ops import FermionOperator
from maya.transforms import jordan_wigner
from maya.utils import count_qubits, eigenspectrum, Grid
from maya.utils._jellium import (
    dual_basis_jellium_model,
    dual_basis_kinetic,
    dual_basis_potential,
    jellium_model,
    jordan_wigner_dual_basis_jellium,
    momentum_vector,
    orbital_id,
    OrbitalSpecificationError,
    plane_wave_kinetic,
    plane_wave_potential,
    position_vector,
)

from divya.ops import QubitOperator


class JelliumTest(unittest.TestCase):

    def test_orbital_id(self):

        # Test in 1D with spin.
        grid = Grid(dimensions=1, length=5, scale=1.0)
        input_coords = [0, 1, 2, 3, 4]
        tensor_factors_up = [1, 3, 5, 7, 9]
        tensor_factors_down = [0, 2, 4, 6, 8]

        test_output_up = [orbital_id(grid, i, 1) for i in input_coords]
        test_output_down = [orbital_id(grid, i, 0) for i in input_coords]

        self.assertEqual(test_output_up, tensor_factors_up)
        self.assertEqual(test_output_down, tensor_factors_down)

        with self.assertRaises(OrbitalSpecificationError):
            orbital_id(grid, 6, 1)

        # Test in 2D without spin.
        grid = Grid(dimensions=2, length=3, scale=1.0)
        input_coords = [(0, 0), (0, 1), (1, 2)]
        tensor_factors = [0, 3, 7]
        test_output = [orbital_id(grid, i) for i in input_coords]
        self.assertEqual(test_output, tensor_factors)

    def test_position_vector(self):

        # Test in 1D.
        grid = Grid(dimensions=1, length=4, scale=4.)
        test_output = [position_vector(i, grid)
                       for i in range(grid.length)]
        correct_output = [-2, -1, 0, 1]
        self.assertEqual(correct_output, test_output)

        grid = Grid(dimensions=1, length=11, scale=2. * numpy.pi)
        for i in range(grid.length):
            self.assertAlmostEqual(
                -position_vector(i, grid),
                position_vector(grid.length - i - 1, grid))

        # Test in 2D.
        grid = Grid(dimensions=2, length=3, scale=3.)
        test_input = []
        test_output = []
        for i in range(3):
            for j in range(3):
                test_input += [(i, j)]
                test_output += [position_vector((i, j), grid)]
        correct_output = numpy.array([[-1., -1.], [-1., 0.], [-1., 1.],
                                      [0., -1.], [0., 0.], [0., 1.],
                                      [1., -1.], [1., 0.], [1., 1.]])
        self.assertAlmostEqual(0., numpy.amax(test_output - correct_output))

    def test_momentum_vector(self):
        grid = Grid(dimensions=1, length=3, scale=2. * numpy.pi)
        test_output = [momentum_vector(i, grid)
                       for i in range(grid.length)]
        correct_output = [-1., 0, 1.]
        self.assertEqual(correct_output, test_output)

        grid = Grid(dimensions=1, length=11, scale=2. * numpy.pi)
        for i in range(grid.length):
            self.assertAlmostEqual(
                -momentum_vector(i, grid),
                momentum_vector(grid.length - i - 1, grid))

        # Test in 2D.
        grid = Grid(dimensions=2, length=3, scale=2. * numpy.pi)
        test_input = []
        test_output = []
        for i in range(3):
            for j in range(3):
                test_input += [(i, j)]
                test_output += [momentum_vector((i, j), grid)]
        correct_output = numpy.array([[-1, -1], [-1, 0], [-1, 1],
                                      [0, -1], [0, 0], [0, 1],
                                      [1, -1], [1, 0], [1, 1]])
        self.assertAlmostEqual(0., numpy.amax(test_output - correct_output))

    def test_kinetic_integration(self):

        # Compute kinetic energy operator in both momentum and position space.
        grid = Grid(dimensions=2, length=2, scale=3.)
        spinless = False
        momentum_kinetic = plane_wave_kinetic(grid, spinless)
        position_kinetic = dual_basis_kinetic(grid, spinless)

        # Diagonalize and confirm the same energy.
        jw_momentum = jordan_wigner(momentum_kinetic)
        jw_position = jordan_wigner(position_kinetic)
        momentum_spectrum = eigenspectrum(jw_momentum)
        position_spectrum = eigenspectrum(jw_position)

        # Confirm spectra are the same.
        difference = numpy.amax(
            numpy.absolute(momentum_spectrum - position_spectrum))
        self.assertAlmostEqual(difference, 0.)

    def test_potential_integration(self):

        # Compute potential energy operator in momentum and position space.
        grid = Grid(dimensions=2, length=3, scale=2.)
        spinless = 1
        momentum_potential = plane_wave_potential(grid, spinless)
        position_potential = dual_basis_potential(grid, spinless)

        # Diagonalize and confirm the same energy.
        jw_momentum = jordan_wigner(momentum_potential)
        jw_position = jordan_wigner(position_potential)
        momentum_spectrum = eigenspectrum(jw_momentum)
        position_spectrum = eigenspectrum(jw_position)

        # Confirm spectra are the same.
        difference = numpy.amax(
            numpy.absolute(momentum_spectrum - position_spectrum))
        self.assertAlmostEqual(difference, 0.)

    def test_model_integration(self):

        # Compute Hamiltonian in both momentum and position space.
        grid = Grid(dimensions=2, length=3, scale=1.0)
        spinless = True
        momentum_hamiltonian = jellium_model(grid, spinless, True)
        position_hamiltonian = jellium_model(grid, spinless, False)

        # Diagonalize and confirm the same energy.
        jw_momentum = jordan_wigner(momentum_hamiltonian)
        jw_position = jordan_wigner(position_hamiltonian)
        momentum_spectrum = eigenspectrum(jw_momentum)
        position_spectrum = eigenspectrum(jw_position)

        # Confirm spectra are the same.
        difference = numpy.amax(
            numpy.absolute(momentum_spectrum - position_spectrum))
        self.assertAlmostEqual(difference, 0.)

    def test_model_integration_with_constant(self):
        # Compute Hamiltonian in both momentum and position space.
        length_scale = 0.7

        grid = Grid(dimensions=2, length=3, scale=length_scale)
        spinless = True

        # Include the Madelung constant in the momentum but not the position
        # Hamiltonian.
        momentum_hamiltonian = jellium_model(grid, spinless, True,
                                             include_constant=True)
        position_hamiltonian = jellium_model(grid, spinless, False)

        # Diagonalize and confirm the same energy.
        jw_momentum = jordan_wigner(momentum_hamiltonian)
        jw_position = jordan_wigner(position_hamiltonian)
        momentum_spectrum = eigenspectrum(jw_momentum)
        position_spectrum = eigenspectrum(jw_position)

        # Confirm momentum spectrum is shifted 2.8372 / length_scale higher.
        max_difference = numpy.amax(momentum_spectrum - position_spectrum)
        min_difference = numpy.amax(momentum_spectrum - position_spectrum)
        self.assertAlmostEqual(max_difference, 2.8372 / length_scale)
        self.assertAlmostEqual(min_difference, 2.8372 / length_scale)

    def test_coefficients(self):

        # Test that the coefficients post-JW transform are as claimed in paper.
        grid = Grid(dimensions=2, length=3, scale=2.)
        spinless = 1
        n_orbitals = grid.num_points()
        n_qubits = (2 ** (1 - spinless)) * n_orbitals
        volume = grid.volume_scale()

        # Kinetic operator.
        kinetic = dual_basis_kinetic(grid, spinless)
        qubit_kinetic = jordan_wigner(kinetic)

        # Potential operator.
        potential = dual_basis_potential(grid, spinless)
        qubit_potential = jordan_wigner(potential)

        # Check identity.
        identity = tuple()
        kinetic_coefficient = qubit_kinetic.terms[identity]
        potential_coefficient = qubit_potential.terms[identity]

        paper_kinetic_coefficient = 0.
        paper_potential_coefficient = 0.
        for indices in grid.all_points_indices():
            momenta = momentum_vector(indices, grid)
            paper_kinetic_coefficient += float(
                n_qubits) * momenta.dot(momenta) / float(4. * n_orbitals)

            if momenta.any():
                potential_contribution = -numpy.pi * float(n_qubits) / float(
                    2. * momenta.dot(momenta) * volume)
                paper_potential_coefficient += potential_contribution

        self.assertAlmostEqual(
            kinetic_coefficient, paper_kinetic_coefficient)
        self.assertAlmostEqual(
            potential_coefficient, paper_potential_coefficient)

        # Check Zp.
        for p in range(n_qubits):
            zp = ((p, 'Z'),)
            kinetic_coefficient = qubit_kinetic.terms[zp]
            potential_coefficient = qubit_potential.terms[zp]

            paper_kinetic_coefficient = 0.
            paper_potential_coefficient = 0.
            for indices in grid.all_points_indices():
                momenta = momentum_vector(indices, grid)
                paper_kinetic_coefficient -= momenta.dot(
                    momenta) / float(4. * n_orbitals)

                if momenta.any():
                    potential_contribution = numpy.pi / float(
                        momenta.dot(momenta) * volume)
                    paper_potential_coefficient += potential_contribution

            self.assertAlmostEqual(
                kinetic_coefficient, paper_kinetic_coefficient)
            self.assertAlmostEqual(
                potential_coefficient, paper_potential_coefficient)

        # Check Zp Zq.
        if spinless:
            spins = [None]
        else:
            spins = [0, 1]

        for indices_a in grid.all_points_indices():
            for indices_b in grid.all_points_indices():

                paper_kinetic_coefficient = 0.
                paper_potential_coefficient = 0.

                position_a = position_vector(indices_a, grid)
                position_b = position_vector(indices_b, grid)
                differences = position_b - position_a

                for spin_a in spins:
                    for spin_b in spins:

                        p = orbital_id(grid, indices_a, spin_a)
                        q = orbital_id(grid, indices_b, spin_b)

                        if p == q:
                            continue

                        zpzq = ((min(p, q), 'Z'), (max(p, q), 'Z'))
                        if zpzq in qubit_potential.terms:
                            potential_coefficient = qubit_potential.terms[zpzq]

                        for indices_c in grid.all_points_indices():
                            momenta = momentum_vector(indices_c, grid)

                            if momenta.any():
                                potential_contribution = numpy.pi * numpy.cos(
                                    differences.dot(momenta)) / float(
                                    momenta.dot(momenta) * volume)
                                paper_potential_coefficient += (
                                    potential_contribution)

                        self.assertAlmostEqual(
                            potential_coefficient, paper_potential_coefficient)

    def test_jordan_wigner_dual_basis_jellium(self):
        # Parameters.
        grid = Grid(dimensions=2, length=3, scale=1.)
        spinless = True

        # Compute fermionic Hamiltonian. Include then subtract constant.
        fermion_hamiltonian = dual_basis_jellium_model(
            grid, spinless, include_constant=True)
        qubit_hamiltonian = jordan_wigner(fermion_hamiltonian)
        qubit_hamiltonian -= QubitOperator((), 2.8372)

        # Compute Jordan-Wigner Hamiltonian.
        test_hamiltonian = jordan_wigner_dual_basis_jellium(grid, spinless)

        # Make sure Hamiltonians are the same.
        self.assertTrue(test_hamiltonian.isclose(qubit_hamiltonian))

        # Check number of terms.
        n_qubits = count_qubits(qubit_hamiltonian)
        if spinless:
            paper_n_terms = 1 - .5 * n_qubits + 1.5 * (n_qubits ** 2)

        num_nonzeros = sum(1 for coeff in qubit_hamiltonian.terms.values() if
                           coeff != 0.0)
        self.assertTrue(num_nonzeros <= paper_n_terms)

    def test_jordan_wigner_dual_basis_jellium_constant_shift(self):
        length_scale = 0.6
        grid = Grid(dimensions=2, length=3, scale=length_scale)
        spinless = True

        hamiltonian_without_constant = jordan_wigner_dual_basis_jellium(
            grid, spinless, include_constant=False)
        hamiltonian_with_constant = jordan_wigner_dual_basis_jellium(
            grid, spinless, include_constant=True)

        difference = hamiltonian_with_constant - hamiltonian_without_constant
        expected = FermionOperator.identity() * (2.8372 / length_scale)

        self.assertTrue(expected.isclose(difference))