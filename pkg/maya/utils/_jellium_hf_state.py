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

"""This module constructs the uniform electron gas' Hartree-Fock state."""
from __future__ import absolute_import

from maya.ops import FermionOperator, normal_ordered
from maya.utils import (count_qubits, jellium_model,
                            inverse_fourier_transform, plane_wave_kinetic)

from scipy.sparse import csr_matrix

import numpy

def lowest_single_particle_energy_states(hamiltonian, n_states):
    """Find the lowest single-particle states of the given Hamiltonian.

    Args:
        hamiltonian (FermionOperator)
        n_states (int): Number of lowest energy states to give."""
    # Enumerate the single-particle states.
    n_single_particle_states = count_qubits(hamiltonian)

    # Compute the energies for each of the single-particle states.
    single_particle_energies = numpy.zeros(n_single_particle_states,
                                           dtype=float)
    for i in range(n_single_particle_states):
        single_particle_energies[i] = hamiltonian.terms.get(
            ((i, 1), (i, 0)), 0.0)

    # Find the n_states lowest states.
    occupied_states = single_particle_energies.argsort()[:n_states]

    return list(occupied_states)


def hartree_fock_state_jellium(grid, n_electrons, spinless=True,
                               plane_wave=False):
    """Give the Hartree-Fock state of jellium.

    Args:
        grid (Grid): The discretization to use.
        n_electrons (int): Number of electrons in the system.
        spinless (bool): Whether to use the spinless model or not.
        plane_wave (bool): Whether to return the Hartree-Fock state in
                           the plane wave (True) or dual basis (False).

    Notes:
        The jellium model is built up by filling the lowest-energy
        single-particle states in the plane-wave Hamiltonian until
        n_electrons states are filled.
    """
    # Get the jellium Hamiltonian in the plane wave basis.
    # For determining the Hartree-Fock state in the PW basis, only the
    # kinetic energy terms matter.
    hamiltonian = plane_wave_kinetic(grid, spinless=spinless)
    hamiltonian = normal_ordered(hamiltonian)
    hamiltonian.compress()

    # The number of occupied single-particle states is the number of electrons.
    # Those states with the lowest single-particle energies are occupied first.
    occupied_states = lowest_single_particle_energy_states(
        hamiltonian, n_electrons)
    occupied_states = numpy.array(occupied_states)

    if plane_wave:
        # In the plane wave basis the HF state is a single determinant.
        hartree_fock_state_index = numpy.sum(2 ** occupied_states)
        hartree_fock_state = csr_matrix(
            ([1.0], ([hartree_fock_state_index], [0])),
            shape=(2 ** count_qubits(hamiltonian), 1))

    else:
        # Inverse Fourier transform the creation operators for the state to get
        # to the dual basis state, then use that to get the dual basis state.
        hartree_fock_state_creation_operator = FermionOperator.identity()
        for state in occupied_states[::-1]:
            hartree_fock_state_creation_operator *= (
                FermionOperator(((int(state), 1),)))
        dual_basis_hf_creation_operator = inverse_fourier_transform(
            hartree_fock_state_creation_operator, grid, spinless)

        dual_basis_hf_creation = normal_ordered(
            dual_basis_hf_creation_operator)

        # Initialize the HF state as a sparse matrix.
        hartree_fock_state = csr_matrix(
            ([], ([], [])), shape=(2 ** count_qubits(hamiltonian), 1),
            dtype=complex)

        # Populate the elements of the HF state in the dual basis.
        for term in dual_basis_hf_creation.terms:
            index = 0
            for operator in term:
                index += 2 ** operator[0]
            hartree_fock_state[index, 0] = dual_basis_hf_creation.terms[term]

    return hartree_fock_state