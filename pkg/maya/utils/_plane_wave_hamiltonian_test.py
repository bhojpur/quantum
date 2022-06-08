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

"""Tests for plane_wave_hamiltonian.py"""
from __future__ import absolute_import

import unittest

import numpy

from maya.ops import normal_ordered
from maya.transforms import jordan_wigner
from maya.utils import eigenspectrum, Grid, jellium_model
from maya.utils._plane_wave_hamiltonian import (
    dual_basis_external_potential,
    fourier_transform,
    inverse_fourier_transform,
    jordan_wigner_dual_basis_hamiltonian,
    plane_wave_external_potential,
    plane_wave_hamiltonian,
    wigner_seitz_length_scale,
)

class PlaneWaveHamiltonianTest(unittest.TestCase):

    def test_wigner_seitz_radius_1d(self):
        wigner_seitz_radius = 3.17
        n_particles = 20
        one_d_test = wigner_seitz_length_scale(
            wigner_seitz_radius, n_particles, 1)
        self.assertAlmostEqual(
            one_d_test, n_particles * 2. * wigner_seitz_radius)

    def test_wigner_seitz_radius_2d(self):
        wigner_seitz_radius = 0.5
        n_particles = 3
        two_d_test = wigner_seitz_length_scale(
            wigner_seitz_radius, n_particles, 2) ** 2.
        self.assertAlmostEqual(
            two_d_test, n_particles * numpy.pi * wigner_seitz_radius ** 2.)

    def test_wigner_seitz_radius_3d(self):
        wigner_seitz_radius = 4.6
        n_particles = 37
        three_d_test = wigner_seitz_length_scale(
            wigner_seitz_radius, n_particles, 3) ** 3.
        self.assertAlmostEqual(
            three_d_test, n_particles * (4. * numpy.pi / 3. *
                                         wigner_seitz_radius ** 3.))

    def test_wigner_seitz_radius_6d(self):
        wigner_seitz_radius = 5.
        n_particles = 42
        six_d_test = wigner_seitz_length_scale(
            wigner_seitz_radius, n_particles, 6) ** 6
        self.assertAlmostEqual(
            six_d_test, n_particles * (numpy.pi ** 3 / 6 *
                                       wigner_seitz_radius ** 6))

    def test_wigner_seitz_radius_bad_dimension_not_integer(self):
        with self.assertRaises(ValueError):
            wigner_seitz_length_scale(3, 2, dimension=4.2)

    def test_wigner_seitz_radius_bad_dimension_not_positive(self):
        with self.assertRaises(ValueError):
            wigner_seitz_length_scale(3, 2, dimension=0)

    def test_fourier_transform(self):
        grid = Grid(dimensions=1, scale=1.5, length=3)
        spinless_set = [True, False]
        geometry = [('H', (0,)), ('H', (0.5,))]
        for spinless in spinless_set:
            h_plane_wave = plane_wave_hamiltonian(
                grid, geometry, spinless, True)
            h_dual_basis = plane_wave_hamiltonian(
                grid, geometry, spinless, False)
            h_plane_wave_t = fourier_transform(h_plane_wave, grid, spinless)
            self.assertTrue(normal_ordered(h_plane_wave_t).isclose(
                normal_ordered(h_dual_basis)))

    def test_inverse_fourier_transform_1d(self):
        grid = Grid(dimensions=1, scale=1.5, length=4)
        spinless_set = [True, False]
        geometry = [('H', (0,)), ('H', (0.5,))]
        for spinless in spinless_set:
            h_plane_wave = plane_wave_hamiltonian(
                grid, geometry, spinless, True)
            h_dual_basis = plane_wave_hamiltonian(
                grid, geometry, spinless, False)
            h_dual_basis_t = inverse_fourier_transform(
                h_dual_basis, grid, spinless)
            self.assertTrue(normal_ordered(h_dual_basis_t).isclose(
                normal_ordered(h_plane_wave)))

    def test_inverse_fourier_transform_2d(self):
        grid = Grid(dimensions=2, scale=1.5, length=3)
        spinless = True
        geometry = [('H', (0, 0)), ('H', (0.5, 0.8))]
        h_plane_wave = plane_wave_hamiltonian(grid, geometry, spinless, True)
        h_dual_basis = plane_wave_hamiltonian(grid, geometry, spinless, False)
        h_dual_basis_t = inverse_fourier_transform(
            h_dual_basis, grid, spinless)
        self.assertTrue(normal_ordered(h_dual_basis_t).isclose(
            normal_ordered(h_plane_wave)))

    def test_plane_wave_hamiltonian_integration(self):
        length_set = [3, 4]
        spinless_set = [True, False]
        geometry = [('H', (0,)), ('H', (0.8,))]
        length_scale = 1.1

        for l in length_set:
            for spinless in spinless_set:
                grid = Grid(dimensions=1, scale=length_scale, length=l)
                h_plane_wave = plane_wave_hamiltonian(
                    grid, geometry, spinless, True, include_constant=True)
                h_dual_basis = plane_wave_hamiltonian(grid, geometry, spinless,
                                                      False)
                jw_h_plane_wave = jordan_wigner(h_plane_wave)
                jw_h_dual_basis = jordan_wigner(h_dual_basis)
                h_plane_wave_spectrum = eigenspectrum(jw_h_plane_wave)
                h_dual_basis_spectrum = eigenspectrum(jw_h_dual_basis)

                max_diff = numpy.amax(
                    h_plane_wave_spectrum - h_dual_basis_spectrum)
                min_diff = numpy.amin(
                    h_plane_wave_spectrum - h_dual_basis_spectrum)

                self.assertAlmostEqual(max_diff, 2.8372 / length_scale)
                self.assertAlmostEqual(min_diff, 2.8372 / length_scale)

    def test_plane_wave_hamiltonian_default_to_jellium_with_no_geometry(self):
        grid = Grid(dimensions=1, scale=1.0, length=4)
        self.assertTrue(plane_wave_hamiltonian(grid).isclose(
            jellium_model(grid)))

    def test_plane_wave_hamiltonian_bad_geometry(self):
        grid = Grid(dimensions=1, scale=1.0, length=4)
        with self.assertRaises(ValueError):
            plane_wave_hamiltonian(grid, geometry=[('H', (0, 0, 0))])

    def test_plane_wave_hamiltonian_bad_element(self):
        grid = Grid(dimensions=3, scale=1.0, length=4)
        with self.assertRaises(ValueError):
            plane_wave_hamiltonian(grid, geometry=[('Unobtainium',
                                                    (0, 0, 0))])

    def test_jordan_wigner_dual_basis_hamiltonian(self):
        grid = Grid(dimensions=2, length=3, scale=1.)
        spinless = True
        geometry = [('H', (0, 0)), ('H', (0.5, 0.8))]

        fermion_hamiltonian = plane_wave_hamiltonian(
            grid, geometry, spinless, False, include_constant=True)
        qubit_hamiltonian = jordan_wigner(fermion_hamiltonian)

        test_hamiltonian = jordan_wigner_dual_basis_hamiltonian(
            grid, geometry, spinless, include_constant=True)
        self.assertTrue(test_hamiltonian.isclose(qubit_hamiltonian))

    def test_jordan_wigner_dual_basis_hamiltonian_default_to_jellium(self):
        grid = Grid(dimensions=1, scale=1.0, length=4)
        self.assertTrue(jordan_wigner_dual_basis_hamiltonian(grid).isclose(
            jordan_wigner(jellium_model(grid, plane_wave=False))))

    def test_jordan_wigner_dual_basis_hamiltonian_bad_geometry(self):
        grid = Grid(dimensions=1, scale=1.0, length=4)
        with self.assertRaises(ValueError):
            jordan_wigner_dual_basis_hamiltonian(
                grid, geometry=[('H', (0, 0, 0))])

    def test_jordan_wigner_dual_basis_hamiltonian_bad_element(self):
        grid = Grid(dimensions=3, scale=1.0, length=4)
        with self.assertRaises(ValueError):
            jordan_wigner_dual_basis_hamiltonian(
                grid, geometry=[('Unobtainium', (0, 0, 0))])