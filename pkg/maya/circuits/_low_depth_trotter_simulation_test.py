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

"""Tests for _low_depth_trotter_simulation.py."""
import numpy
import os
import random
import unittest

import divya

from scipy.sparse.linalg import expm

from maya.circuits import _low_depth_trotter_simulation
from maya.ops import FermionOperator, normal_ordered
from maya.transforms import get_sparse_operator
from maya.utils import Grid, plane_wave_hamiltonian

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def ordered_wavefunction(engine, indices_to_evaluate=None):
    """Return the correctly ordered wave function amplitudes.

    Args:
        engine (divya.MainEngine): The engine from which to take the
                                      amplitudes.
        indices_to_evaluate (numpy.array): Array of integer indices to
                                           evaluate amplitudes of. If
                                           indices_to_evaluate is not
                                           set, all amplitudes are
                                           evaluated.
    """
    n_qubits = engine._qubit_idx
    if indices_to_evaluate is None:
        indices_to_evaluate = numpy.arange(2 ** n_qubits)

    indices = numpy.zeros(len(indices_to_evaluate), dtype=int)

    # Get the qubit order dictionary and raw wavefunction from the engine.
    qubit_order_dict, unordered_wavefunction = engine.backend.cheat()

    for bit_number in range(n_qubits):
        # To each logical state for which qubit k is 1, add
        # 2 ** (qubit k's position in the raw wavefunction). This is quickly
        # given by 1 << qubit_order_dict[k].
        indices[(indices_to_evaluate & (1 << bit_number)) != 0] += (
            1 << qubit_order_dict[bit_number])

    # Return the subset of unordered_wavefunction corresponding to the indices.
    return list(map(unordered_wavefunction.__getitem__, indices))


def dual_basis_hamiltonian(n_dimensions, system_size,
                           plane_wave=False, spinless=True):
    """Return the plane wave dual basis hamiltonian with the given parameters.

    Returns: the Hamiltonian as a normal-ordered FermionOperator.

    Args:
        n_dimensions (int): The number of dimensions in the system.
        system_size (int): The side length along each dimension.
        plane_wave (bool): Whether the system is in the plane wave basis.
        spinless (bool): Whether the system is spinless.

    Notes:
        Follows Eq. 10 of https://arxiv.org/pdf/1706.00023.pdf.
    """
    grid = Grid(n_dimensions, length=system_size, scale=1.0 * system_size)
    hamiltonian = plane_wave_hamiltonian(grid, spinless=spinless,
                                         plane_wave=plane_wave)
    return normal_ordered(hamiltonian)


class FourQubitSecondOrderTrotterTest(unittest.TestCase):

    def setUp(self):
        self.size = 4
        self.engine = divya.MainEngine()
        self.register = self.engine.allocate_qureg(self.size)
        random.seed(17)

    def tearDown(self):
        divya.ops.All(divya.ops.Measure) | self.register

    def test_simulate_n0n1(self):
        hamiltonian = FermionOperator('1^ 0^ 1 0')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Use 3^ 2^ 3 2 because get_sparse_operator reverses the indices.
        evol_matrix = expm(-1j * get_sparse_operator(
            FermionOperator('3^ 2^ 3 2'), n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(ordered_wavefunction(self.engine) -
                                expected.T))

    def test_simulate_n0n3(self):
        hamiltonian = FermionOperator('3^ 0^ 3 0')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Though get_sparse_operator reverses the indices, this is symmetric.
        evol_matrix = expm(-1j * get_sparse_operator(
            hamiltonian, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(ordered_wavefunction(self.engine) -
                                expected.T))

    def test_simulate_n1n3(self):
        hamiltonian = FermionOperator('3^ 1^ 3 1')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Use 2^ 0^ 2 0 because get_sparse_operator reverses the indices.
        evol_matrix = expm(-1j * get_sparse_operator(
            FermionOperator('2^ 0^ 2 0'), n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(ordered_wavefunction(self.engine) -
                                expected.T))

    def test_single_trotter_step_no_input_ordering_n1n3(self):
        hamiltonian = FermionOperator('3^ 1^ 3 1')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulation_gate_trotter_step(
            self.register, hamiltonian, first_order=False)
        self.engine.flush()

        # Use 2^ 0^ 2 0 because get_sparse_operator reverses the indices.
        evol_matrix = expm(-1j * get_sparse_operator(
            FermionOperator('2^ 0^ 2 0'), n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(ordered_wavefunction(self.engine) -
                                expected.T))

    def test_simulate_hopping_0_to_1(self):
        hamiltonian = FermionOperator('1^ 0') + FermionOperator('0^ 1')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Use 3^ 2 + 2^ 3 because get_sparse_operator reverses the indices.
        reversed_operator = FermionOperator('3^ 2') + FermionOperator('2^ 3')
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(ordered_wavefunction(self.engine) -
                                expected.T))

    def test_simulate_hopping_1_to_3(self):
        hamiltonian = FermionOperator('1^ 3') + FermionOperator('3^ 1')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Use 0^ 2 + 2^ 0 because get_sparse_operator reverses the indices.
        reversed_operator = FermionOperator('0^ 2') + FermionOperator('2^ 0')
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T))

    def test_simulate_hopping_0_to_3(self):
        hamiltonian = FermionOperator('0^ 3') + FermionOperator('3^ 0')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)
        self.engine.flush()

        # Use 0^ 2 + 2^ 0 because get_sparse_operator reverses the indices.
        evol_matrix = expm(-1j * get_sparse_operator(
            hamiltonian, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T))

    def test_simulate_multiple_hopping_terms(self):
        hamiltonian = (FermionOperator('0^ 3') + FermionOperator('3^ 0') +
                       2 * (FermionOperator('1^ 3') +
                            FermionOperator('3^ 1')) -
                       0.5 * (FermionOperator('0^ 1') +
                              FermionOperator('1^ 0')))

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=4, first_order=False)

        self.engine.flush()

        # get_sparse_operator reverses the indices, so reverse the sites
        # the Hamiltonian acts on so as to compare them.
        reversed_operator = (
            FermionOperator('0^ 3') + FermionOperator('3^ 0') +
            2 * (FermionOperator('0^ 2') + FermionOperator('2^ 0')) -
            0.5 * (FermionOperator('3^ 2') + FermionOperator('2^ 3')))
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T, atol=1e-2))

    def test_simulate_multiple_two_number_terms(self):
        hamiltonian = (0.37 * FermionOperator('1^ 0^ 1 0') +
                       2.4 * FermionOperator('3^ 0^ 3 0') -
                       2 * FermionOperator('3^ 1^ 3 1'))

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)

        self.engine.flush()

        # get_sparse_operator reverses the indices, so reverse the sites
        # the Hamiltonian acts on so as to compare them.
        reversed_operator = (0.37 * FermionOperator('3^ 2^ 3 2') +
                             2.4 * FermionOperator('3^ 0^ 3 0') -
                             2 * FermionOperator('2^ 0^ 2 0'))
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(numpy.array(ordered_wavefunction(self.engine) -
                                            expected.T)))

    def test_simulate_single_and_double_number_terms(self):
        hamiltonian = (0.37 * FermionOperator('1^ 0^ 1 0') +
                       2.4 * FermionOperator('3^ 0^ 3 0') -
                       2 * FermionOperator('3^ 1^ 3 1') +
                       1.1 * FermionOperator('2^ 2') +
                       1.7 * FermionOperator('0^ 0') -
                       0.3 * FermionOperator('3^ 3'))

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=1, first_order=False)

        self.engine.flush()

        # get_sparse_operator reverses the indices, so reverse the sites
        # the Hamiltonian acts on so as to compare them.
        reversed_operator = (0.37 * FermionOperator('3^ 2^ 3 2') +
                             2.4 * FermionOperator('3^ 0^ 3 0') -
                             2 * FermionOperator('2^ 0^ 2 0') +
                             1.1 * FermionOperator('1^ 1') +
                             1.7 * FermionOperator('3^ 3') -
                             0.3 * FermionOperator('0^ 0'))
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T),
                        msg=str(numpy.array(ordered_wavefunction(self.engine) -
                                            expected.T)))

    def test_simulate_overlapping_number_and_hopping_terms(self):
        hamiltonian = (0.37 * FermionOperator('1^ 0^ 1 0') +
                       FermionOperator('2^ 0') + FermionOperator('0^ 2'))

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=2, first_order=False)

        self.engine.flush()

        # get_sparse_operator reverses the indices, so reverse the sites
        # the Hamiltonian acts on so as to compare them.
        reversed_operator = (0.37 * FermionOperator('3^ 2^ 3 2') +
                             FermionOperator('3^ 1') + FermionOperator('1^ 3'))
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T,
                                       atol=1e-2),
                        msg=str(numpy.array(ordered_wavefunction(self.engine) -
                                            expected.T)))

    def test_simulate_dual_basis_hamiltonian(self):
        hamiltonian = dual_basis_hamiltonian(1, self.size)
        self.engine.flush()

        # Choose random state.
        initial_state = numpy.zeros(2 ** self.size, dtype=complex)
        for i in range(len(initial_state)):
            initial_state[i] = (random.random() *
                                numpy.exp(1j * 2 * numpy.pi * random.random()))
        initial_state /= numpy.linalg.norm(initial_state)

        # Put randomly chosen state in the registers.
        self.engine.backend.set_wavefunction(initial_state, self.register)

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=7, first_order=False)

        self.engine.flush()

        # get_sparse_operator reverses the indices, but the jellium
        # Hamiltonian is symmetric.
        evol_matrix = expm(-1j * get_sparse_operator(
            hamiltonian, n_qubits=self.size)).todense()
        initial_state = numpy.matrix(initial_state).T
        expected = evol_matrix * initial_state

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T,
                                       atol=1e-2),
                        msg=str(numpy.array(ordered_wavefunction(self.engine) -
                                            expected.T)))

    def test_simulate_dual_basis_hamiltonian_with_spin_and_potentials(self):
        big_eng = divya.MainEngine()
        big_reg = big_eng.allocate_qureg(2 * self.size)
        hamiltonian = dual_basis_hamiltonian(1, self.size, spinless=False)

        for i in range(2 * self.size):
            coefficient = 1. / (i + 1)
            if i % 3:
                coefficient = -coefficient
            hamiltonian += FermionOperator(((i, 1), (i, 0)), coefficient)

        # Choose random state.
        initial_state = numpy.zeros(2 ** (2 * self.size), dtype=complex)
        for i in range(len(initial_state)):
            initial_state[i] = (random.random() *
                                numpy.exp(1j * 2 * numpy.pi * random.random()))
        initial_state /= numpy.linalg.norm(initial_state)

        # Put randomly chosen state in the registers.
        big_eng.flush()
        big_eng.backend.set_wavefunction(initial_state, big_reg)

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            big_reg, hamiltonian, trotter_steps=7, first_order=False,
            input_ordering=list(range(7, -1, -1)))

        big_eng.flush()

        # get_sparse_operator reverses the indices - we've accounted for this
        # with the reversed input_ordering.
        evol_matrix = expm(-1j * get_sparse_operator(
            hamiltonian, n_qubits=2*self.size)).todense()
        initial_state = numpy.matrix(initial_state).T
        expected = evol_matrix * initial_state

        self.assertTrue(numpy.allclose(ordered_wavefunction(big_eng),
                                       expected.T,
                                       atol=1e-2),
                        msg=str(numpy.array(ordered_wavefunction(big_eng) -
                                            expected.T)))

        divya.ops.All(divya.ops.Measure) | big_reg

    def test_simulate_dual_basis_evolution_bad_input_ordering(self):
        with self.assertRaises(ValueError):
            _low_depth_trotter_simulation.simulate_dual_basis_evolution(
                self.register, FermionOperator(), input_ordering=[1, 2])

    def test_simulate_dual_basis_evolution_n_trotter_steps_not_integer(self):
        with self.assertRaises(ValueError):
            _low_depth_trotter_simulation.simulate_dual_basis_evolution(
                self.register, FermionOperator(), trotter_steps=1.5)

    def test_simulate_dual_basis_evolution_bad_n_trotter_steps(self):
        with self.assertRaises(ValueError):
            _low_depth_trotter_simulation.simulate_dual_basis_evolution(
                self.register, FermionOperator(), trotter_steps=0)


class FourQubitFirstOrderEquivalenceWithSecondOrderTest(unittest.TestCase):

    def setUp(self):
        self.size = 4
        self.engine = divya.MainEngine()
        self.register = self.engine.allocate_qureg(self.size)

    def tearDown(self):
        divya.ops.All(divya.ops.Measure) | self.register

    def test_first_order_odd_number_of_steps_reversal(self):
        hamiltonian = FermionOperator('1^ 3') + FermionOperator('3^ 1')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=3, first_order=True)

        _low_depth_trotter_simulation.fermionic_reorder(
            self.register, range(self.size - 1, -1, -1))
        self.engine.flush()

        # Use 0^ 2 + 2^ 0 because get_sparse_operator reverses the indices.
        reversed_operator = FermionOperator('0^ 2') + FermionOperator('2^ 0')
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T))

    def test_first_order_even_number_of_steps_no_reversal(self):
        hamiltonian = FermionOperator('2^ 3') + FermionOperator('3^ 2')

        divya.ops.All(divya.ops.H) | self.register

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            self.register, hamiltonian, trotter_steps=2, first_order=True)

        self.engine.flush()

        # Use 0^ 1 + 1^ 0 because get_sparse_operator reverses the indices.
        reversed_operator = FermionOperator('0^ 1') + FermionOperator('1^ 0')
        evol_matrix = expm(-1j * get_sparse_operator(
            reversed_operator, n_qubits=self.size)).todense()
        expected = evol_matrix * numpy.matrix([2 ** (-self.size / 2.)] *
                                              2 ** self.size).T

        self.assertTrue(numpy.allclose(ordered_wavefunction(self.engine),
                                       expected.T))


class HighTrotterNumberIntegrationTest(unittest.TestCase):

    def setUp(self):
        random.seed(17)

    def test_trotter_order_does_not_matter_for_high_trotter_number(self):
        size = 4
        hamiltonian = dual_basis_hamiltonian(n_dimensions=1, system_size=size)
        hamiltonian.compress()

        eng1 = divya.MainEngine()
        eng2 = divya.MainEngine()
        reg1 = eng1.allocate_qureg(size)
        reg2 = eng2.allocate_qureg(size)
        eng1.flush()
        eng2.flush()

        # Choose random state.
        state = numpy.zeros(2 ** size, dtype=complex)
        for i in range(len(state)):
            state[i] = (random.random() *
                        numpy.exp(1j * 2 * numpy.pi * random.random()))
        state /= numpy.linalg.norm(state)

        # Put randomly chosen state in the registers.
        eng1.backend.set_wavefunction(state, reg1)
        eng2.backend.set_wavefunction(state, reg2)

        # Swap and change the input ordering for reg1. These operations should
        # cancel each other out.
        divya.ops.Swap | (reg1[1], reg1[2])
        divya.ops.C(divya.ops.Z) | (reg1[1], reg1[2])

        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            reg1, hamiltonian=hamiltonian, trotter_steps=7,
            input_ordering=[0, 2, 1, 3], first_order=False)
        _low_depth_trotter_simulation.simulate_dual_basis_evolution(
            reg2, hamiltonian=hamiltonian, trotter_steps=7, first_order=False)

        # Undo the inital swaps on reg1.
        divya.ops.Swap | (reg1[1], reg1[2])
        divya.ops.C(divya.ops.Z) | (reg1[1], reg1[2])

        divya.ops.All(divya.ops.H) | reg1
        eng1.flush()
        divya.ops.All(divya.ops.H) | reg2
        eng2.flush()

        self.assertTrue(numpy.allclose(ordered_wavefunction(eng1),
                                       ordered_wavefunction(eng2),
                                       atol=1e-2))
        divya.ops.All(divya.ops.Measure) | reg1
        divya.ops.All(divya.ops.Measure) | reg2