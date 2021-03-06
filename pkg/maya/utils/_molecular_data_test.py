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

"""Tests for molecular_data."""
from __future__ import absolute_import

import numpy.random
import scipy.linalg
import unittest

from maya.config import *
from maya.utils import *
from maya.utils._molecular_data import *

class MolecularDataTest(unittest.TestCase):

    def setUp(self):
        self.geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.7414))]
        self.basis = 'sto-3g'
        self.multiplicity = 1
        self.filename = os.path.join(THIS_DIRECTORY, 'data',
                                     'H2_sto-3g_singlet_0.7414')
        self.molecule = MolecularData(
            self.geometry, self.basis, self.multiplicity,
            filename=self.filename)
        self.molecule.load()

    def testUnitConversion(self):
        """Test the unit conversion routines"""
        unit_angstrom = 1.0
        bohr = angstroms_to_bohr(unit_angstrom)
        self.assertAlmostEqual(bohr, 1.889726)
        inverse_transform = bohr_to_angstroms(bohr)
        self.assertAlmostEqual(inverse_transform, 1.0)

    def test_name_molecule(self):
        charge = 0
        correct_name = str('H2_sto-3g_singlet_0.7414')
        computed_name = name_molecule(self.geometry,
                                      self.basis,
                                      self.multiplicity,
                                      charge,
                                      description="0.7414")
        self.assertEqual(correct_name, computed_name)
        self.assertEqual(correct_name, self.molecule.name)

        # Check (+) charge
        charge = 1
        correct_name = "H2_sto-3g_singlet_1+_0.7414"
        computed_name = name_molecule(self.geometry,
                                      self.basis,
                                      self.multiplicity,
                                      charge,
                                      description="0.7414")
        self.assertEqual(correct_name, computed_name)

        # Check errors in naming
        with self.assertRaises(TypeError):
            test_molecule = MolecularData(self.geometry, self.basis,
                                          self.multiplicity, description=5)
        correct_name = str('H2_sto-3g_singlet')
        test_molecule = self.molecule = MolecularData(
            self.geometry, self.basis, self.multiplicity,
            data_directory=DATA_DIRECTORY)
        self.assertSequenceEqual(correct_name, test_molecule.name)

    def test_invalid_multiplicity(self):
        geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.7414))]
        basis = 'sto-3g'
        multiplicity = -1
        with self.assertRaises(MoleculeNameError):
            molecule = MolecularData(
                geometry, basis, multiplicity)

    def test_geometry_from_file(self):
        water_geometry = [('O', (0., 0., 0.)),
                          ('H', (0.757, 0.586, 0.)),
                          ('H', (-.757, 0.586, 0.))]
        filename = os.path.join(THIS_DIRECTORY, 'data', 'geometry_example.txt')
        test_geometry = geometry_from_file(filename)
        for atom in range(3):
            self.assertAlmostEqual(water_geometry[atom][0],
                                   test_geometry[atom][0])
            for coordinate in range(3):
                self.assertAlmostEqual(water_geometry[atom][1][coordinate],
                                       test_geometry[atom][1][coordinate])

    def test_save_load(self):
        n_atoms = self.molecule.n_atoms
        orbitals = self.molecule.canonical_orbitals
        self.assertFalse(orbitals is None)
        self.molecule.n_atoms += 1
        self.assertEqual(self.molecule.n_atoms, n_atoms + 1)
        self.molecule.load()
        self.assertEqual(self.molecule.n_atoms, n_atoms)
        dummy_data = self.molecule.get_from_file("dummy_entry")
        self.assertTrue(dummy_data is None)

    def test_dummy_save(self):

        # Make fake molecule.
        filename = os.path.join(THIS_DIRECTORY, 'data', 'dummy_molecule')
        geometry = [('H', (0., 0., 0.)), ('H', (0., 0., 0.7414))]
        basis = '6-31g*'
        multiplicity = 7
        charge = -1
        description = 'paya_forever'
        molecule = MolecularData(geometry, basis, multiplicity,
                                 charge, description, filename)

        # Make some attributes to save.
        molecule.n_orbitals = 10
        molecule.n_qubits = 10
        molecule.nuclear_repulsion = -12.3
        molecule.hf_energy = 99.
        molecule.canonical_orbitals = [1, 2, 3, 4]
        molecule.orbital_energies = [5, 6, 7, 8]
        molecule.one_body_integrals = [5, 6, 7, 8]
        molecule.two_body_integrals = [5, 6, 7, 8]
        molecule.mp2_energy = -12.
        molecule.cisd_energy = 32.
        molecule.cisd_one_rdm = numpy.arange(10)
        molecule.cisd_two_rdm = numpy.arange(10)
        molecule.fci_energy = 232.
        molecule.fci_one_rdm = numpy.arange(11)
        molecule.fci_two_rdm = numpy.arange(11)
        molecule.ccsd_energy = 88.
        molecule.ccsd_single_amps = [1, 2, 3]
        molecule.ccsd_double_amps = [1, 2, 3]

        # Test missing calculation and information exceptions
        molecule.hf_energy = None
        with self.assertRaises(MissingCalculationError):
            one_body_ints, two_body_ints = molecule.get_integrals()
        molecule.hf_energy = 99.

        with self.assertRaises(ValueError):
            molecule.get_active_space_integrals([], [])

        molecule.fci_energy = None
        with self.assertRaises(MissingCalculationError):
            molecule.get_molecular_rdm(use_fci=True)
        molecule.fci_energy = 232.

        molecule.cisd_energy = None
        with self.assertRaises(MissingCalculationError):
            molecule.get_molecular_rdm(use_fci=False)
        molecule.cisd_energy = 232.

        # Save molecule.
        molecule.save()

        try:
            # Change attributes and load.
            molecule.ccsd_energy = -2.232

            # Load molecule.
            new_molecule = MolecularData(filename=filename)
            molecule.load()

            # Tests re-load functionality
            molecule.save()

            # Check CCSD energy.
            self.assertAlmostEqual(new_molecule.ccsd_energy,
                                   molecule.ccsd_energy)
            self.assertAlmostEqual(molecule.ccsd_energy, 88.)
        finally:
            os.remove(filename + '.hdf5')

    def test_file_loads(self):
        """Test different filename specs"""
        data_directory = os.path.join(THIS_DIRECTORY, 'data')
        molecule = MolecularData(
            self.geometry, self.basis, self.multiplicity,
            filename=self.filename)
        test_hf_energy = molecule.hf_energy
        molecule = MolecularData(
            self.geometry, self.basis, self.multiplicity,
            filename=self.filename + ".hdf5",
            data_directory=data_directory)
        self.assertAlmostEqual(test_hf_energy, molecule.hf_energy)

        molecule = MolecularData(filename=self.filename + ".hdf5")
        integrals = molecule.one_body_integrals
        self.assertTrue(integrals is not None)

        with self.assertRaises(ValueError):
            MolecularData()

    def test_active_space(self):
        """Test simple active space truncation features"""

        # Start w/ no truncation
        core_const, one_body_integrals, two_body_integrals = (
            self.molecule.get_active_space_integrals(active_indices=[0, 1]))

        self.assertAlmostEqual(core_const, 0.0)
        self.assertAlmostEqual(scipy.linalg.norm(one_body_integrals -
                               self.molecule.one_body_integrals), 0.0)
        self.assertAlmostEqual(scipy.linalg.norm(two_body_integrals -
                               self.molecule.two_body_integrals), 0.0)

    def test_energies(self):
        self.assertAlmostEqual(self.molecule.hf_energy, -1.1167, places=4)
        self.assertAlmostEqual(self.molecule.mp2_energy, -1.1299, places=4)
        self.assertAlmostEqual(self.molecule.cisd_energy, -1.1373, places=4)
        self.assertAlmostEqual(self.molecule.ccsd_energy, -1.1373, places=4)
        self.assertAlmostEqual(self.molecule.ccsd_energy, -1.1373, places=4)

    def test_rdm_and_rotation(self):

        # Compute total energy from RDM.
        molecular_hamiltonian = self.molecule.get_molecular_hamiltonian()
        molecular_rdm = self.molecule.get_molecular_rdm()
        total_energy = molecular_rdm.expectation(molecular_hamiltonian)
        self.assertAlmostEqual(total_energy, self.molecule.cisd_energy)

        # Build random rotation with correction dimension.
        num_spatial_orbitals = self.molecule.n_orbitals
        rotation_generator = numpy.random.randn(
            num_spatial_orbitals, num_spatial_orbitals)
        rotation_matrix = scipy.linalg.expm(
            rotation_generator - rotation_generator.T)

        # Compute total energy from RDM under some basis set rotation.
        molecular_rdm.rotate_basis(rotation_matrix)
        molecular_hamiltonian.rotate_basis(rotation_matrix)
        total_energy = molecular_rdm.expectation(molecular_hamiltonian)
        self.assertAlmostEqual(total_energy, self.molecule.cisd_energy)

    def test_get_up_down_electrons(self):
        largest_atom = 20
        for n_electrons in range(1, largest_atom):

            # Make molecule.
            basis = 'sto-3g'
            atom_name = periodic_table[n_electrons]
            molecule = make_atom(atom_name, basis)

            # Get expected alpha and beta.
            spin = periodic_polarization[n_electrons] / 2.
            multiplicity = int(2 * spin + 1)
            expected_alpha = n_electrons / 2 + (multiplicity - 1)
            expected_beta = n_electrons / 2 - (multiplicity - 1)

            # Test.
            self.assertAlmostEqual(molecule.get_n_alpha_electrons(),
                                   expected_alpha)
            self.assertAlmostEqual(molecule.get_n_beta_electrons(),
                                   expected_beta)


if __name__ == '__main__':
    unittest.main()