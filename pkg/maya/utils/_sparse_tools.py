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

"""This module provides functions to interface with scipy.sparse."""
from __future__ import absolute_import

from functools import reduce
from future.utils import iteritems

import itertools
import numpy
import numpy.linalg
import scipy
import scipy.sparse
import scipy.sparse.linalg

from maya.config import *
from maya.ops import FermionOperator, hermitian_conjugated, normal_ordered
from maya.utils import fourier_transform, Grid
from maya.utils._jellium import (momentum_vector, position_vector,
                                     grid_indices)

from divya.ops import QubitOperator


# Make global definitions.
identity_csc = scipy.sparse.identity(2, format='csr', dtype=complex)
pauli_x_csc = scipy.sparse.csc_matrix([[0., 1.], [1., 0.]], dtype=complex)
pauli_y_csc = scipy.sparse.csc_matrix([[0., -1.j], [1.j, 0.]], dtype=complex)
pauli_z_csc = scipy.sparse.csc_matrix([[1., 0.], [0., -1.]], dtype=complex)
q_raise_csc = (pauli_x_csc - 1.j * pauli_y_csc) / 2.
q_lower_csc = (pauli_x_csc + 1.j * pauli_y_csc) / 2.
pauli_matrix_map = {'I': identity_csc, 'X': pauli_x_csc,
                    'Y': pauli_y_csc, 'Z': pauli_z_csc}


def wrapped_kronecker(operator_1, operator_2):
    """Return the Kronecker product of two sparse.csc_matrix operators."""
    return scipy.sparse.kron(operator_1, operator_2, 'csc')


def kronecker_operators(*args):
    """Return the Kronecker product of multiple sparse.csc_matrix operators."""
    return reduce(wrapped_kronecker, *args)


def jordan_wigner_ladder_sparse(n_qubits, tensor_factor, ladder_type):
    """Make a matrix representation of a fermion ladder operator.

    Args:
        index: This is a nonzero integer. The integer indicates the tensor
            factor and the sign indicates raising or lowering.
        n_qubits(int): Number qubits in the system Hilbert space.

    Returns:
        The corresponding SparseOperator.
    """
    identities = [scipy.sparse.identity(
        2 ** tensor_factor, dtype=complex, format='csc')]
    parities = (n_qubits - tensor_factor - 1) * [pauli_z_csc]
    if ladder_type:
        operator = kronecker_operators(identities + [q_raise_csc] + parities)
    else:
        operator = kronecker_operators(identities + [q_lower_csc] + parities)
    return operator


def jordan_wigner_sparse(fermion_operator, n_qubits=None):
    """Initialize a SparseOperator from a FermionOperator.

    Args:
        fermion_operator(FermionOperator): instance of the FermionOperator
            class.
        n_qubits(int): Number of qubits.

    Returns:
        The corresponding SparseOperator.
    """
    if n_qubits is None:
        from maya.utils import count_qubits
        n_qubits = count_qubits(fermion_operator)

    # Create a list of raising and lowering operators for each orbital.
    jw_operators = []
    for tensor_factor in range(n_qubits):
        jw_operators += [(jordan_wigner_ladder_sparse(n_qubits,
                                                      tensor_factor,
                                                      0),
                          jordan_wigner_ladder_sparse(n_qubits,
                                                      tensor_factor,
                                                      1))]

    # Construct the SparseOperator.
    n_hilbert = 2 ** n_qubits
    values_list = [[]]
    row_list = [[]]
    column_list = [[]]
    for term in fermion_operator.terms:
        coefficient = fermion_operator.terms[term]
        sparse_matrix = coefficient * scipy.sparse.identity(
            2 ** n_qubits, dtype=complex, format='csc')
        for ladder_operator in term:
            sparse_matrix = sparse_matrix * jw_operators[
                ladder_operator[0]][ladder_operator[1]]

        if coefficient:
            # Extract triplets from sparse_term.
            sparse_matrix = sparse_matrix.tocoo(copy=False)
            values_list.append(sparse_matrix.data)
            (row, column) = sparse_matrix.nonzero()
            row_list.append(row)
            column_list.append(column)

    values_list = numpy.concatenate(values_list)
    row_list = numpy.concatenate(row_list)
    column_list = numpy.concatenate(column_list)
    sparse_operator = scipy.sparse.coo_matrix((
        values_list, (row_list, column_list)),
        shape=(n_hilbert, n_hilbert)).tocsc(copy=False)
    sparse_operator.eliminate_zeros()
    return sparse_operator


def qubit_operator_sparse(qubit_operator, n_qubits=None):
    """Initialize a SparseOperator from a QubitOperator.

    Args:
        qubit_operator(QubitOperator): instance of the QubitOperator class.
        n_qubits (int): Number of qubits.

    Returns:
        The corresponding SparseOperator.
    """
    from maya.utils import count_qubits
    if n_qubits is None:
        n_qubits = count_qubits(qubit_operator)
    if n_qubits < count_qubits(qubit_operator):
        raise ValueError('Invalid number of qubits specified.')

    # Construct the SparseOperator.
    n_hilbert = 2 ** n_qubits
    values_list = [[]]
    row_list = [[]]
    column_list = [[]]

    # Loop through the terms.
    for qubit_term in qubit_operator.terms:
        tensor_factor = 0
        coefficient = qubit_operator.terms[qubit_term]
        sparse_operators = [coefficient]
        for pauli_operator in qubit_term:

            # Grow space for missing identity operators.
            if pauli_operator[0] > tensor_factor:
                identity_qubits = pauli_operator[0] - tensor_factor
                identity = scipy.sparse.identity(
                    2 ** identity_qubits, dtype=complex, format='csc')
                sparse_operators += [identity]

            # Add actual operator to the list.
            sparse_operators += [pauli_matrix_map[pauli_operator[1]]]
            tensor_factor = pauli_operator[0] + 1

        # Grow space at end of string unless operator acted on final qubit.
        if tensor_factor < n_qubits or not qubit_term:
            identity_qubits = n_qubits - tensor_factor
            identity = scipy.sparse.identity(
                2 ** identity_qubits, dtype=complex, format='csc')
            sparse_operators += [identity]

        # Extract triplets from sparse_term.
        sparse_matrix = kronecker_operators(sparse_operators)
        values_list.append(sparse_matrix.tocoo(copy=False).data)
        (column, row) = sparse_matrix.nonzero()
        column_list.append(column)
        row_list.append(row)

    # Create sparse operator.
    values_list = numpy.concatenate(values_list)
    row_list = numpy.concatenate(row_list)
    column_list = numpy.concatenate(column_list)
    sparse_operator = scipy.sparse.coo_matrix((
        values_list, (row_list, column_list)),
        shape=(n_hilbert, n_hilbert)).tocsc(copy=False)
    sparse_operator.eliminate_zeros()
    return sparse_operator


def jw_hartree_fock_state(n_electrons, n_orbitals):
    """Function to product Hartree-Fock state in JW representation."""
    occupied = scipy.sparse.csr_matrix([[0], [1]], dtype=float)
    psi = 1.
    unoccupied = scipy.sparse.csr_matrix([[1], [0]], dtype=float)
    for orbital in range(n_electrons):
        psi = scipy.sparse.kron(psi, occupied, 'csr')
    for orbital in range(n_orbitals - n_electrons):
        psi = scipy.sparse.kron(psi, unoccupied, 'csr')
    return psi


def jw_number_indices(n_electrons, n_qubits):
    """Return the indices for n_electrons in n_qubits under JW encoding

    Calculates the indices for all possible arrangements of n-electrons
        within n-qubit orbitals when a Jordan-Wigner encoding is used.
        Useful for restricting generic operators or vectors to a particular
        particle number space when desired

    Args:
        n_electrons(int): Number of particles to restrict the operator to
        n_qubits(int): Number of qubits defining the total state

    Returns:
        indices(list): List of indices in a 2^n length array that indicate
            the indices of constant particle number within n_qubits
            in a Jordan-Wigner encoding.

    """
    occupations = itertools.combinations(range(n_qubits), n_electrons)
    indices = [sum([2**n for n in occupation])
               for occupation in occupations]
    return indices


def jw_number_restrict_operator(operator, n_electrons, n_qubits=None):
    """Restrict a Jordan-Wigner encoded operator to a given particle number

    Args:
        sparse_operator(ndarray or sparse): Numpy operator acting on
            the space of n_qubits.
        n_electrons(int): Number of particles to restrict the operator to
        n_qubits(int): Number of qubits defining the total state

    Returns:
        new_operator(ndarray or sparse): Numpy operator restricted to
            acting on states with the same particle number.
    """
    if n_qubits is None:
        n_qubits = int(numpy.log2(operator.shape[0]))

    select_indices = jw_number_indices(n_electrons, n_qubits)
    return operator[numpy.ix_(select_indices, select_indices)]


def get_density_matrix(states, probabilities):
    n_qubits = states[0].shape[0]
    density_matrix = scipy.sparse.csc_matrix(
        (n_qubits, n_qubits), dtype=complex)
    for state, probability in zip(states, probabilities):
        density_matrix = density_matrix + probability * state * state.getH()
    return density_matrix


def is_hermitian(sparse_operator):
    """Test if matrix is Hermitian."""
    difference = sparse_operator - sparse_operator.getH()
    if difference.nnz:
        discrepancy = max(map(abs, difference.data))
        if discrepancy > EQ_TOLERANCE:
            return False
    return True


def get_ground_state(sparse_operator):
    """Compute lowest eigenvalue and eigenstate.

    Returns:
        eigenvalue: The lowest eigenvalue, a float.
        eigenstate: The lowest eigenstate in scipy.sparse csc format.
    """
    if not is_hermitian(sparse_operator):
        raise ValueError('sparse_operator must be Hermitian.')

    values, vectors = scipy.sparse.linalg.eigsh(
        sparse_operator, 2, which='SA', maxiter=1e7)

    eigenstate = scipy.sparse.csc_matrix(vectors[:, 0])
    eigenvalue = values[0]
    return eigenvalue, eigenstate.getH()


def sparse_eigenspectrum(sparse_operator):
    """Perform a dense diagonalization.

    Returns:
        eigenspectrum: The lowest eigenvalues in a numpy array.
    """
    dense_operator = sparse_operator.todense()
    if is_hermitian(sparse_operator):
        eigenspectrum = numpy.linalg.eigvalsh(dense_operator)
    else:
        eigenspectrum = numpy.linalg.eigvals(dense_operator)
    return numpy.sort(eigenspectrum)


def expectation(sparse_operator, state):
    """Compute expectation value of operator with a state.

    Args:
        state: scipy.sparse.csc vector representing a pure state,
            or, a scipy.sparse.csc matrix representing a density matrix.

    Returns:
        A real float giving expectation value.

    Raises:
        ValueError: Input state has invalid format.
    """
    # Handle density matrix.
    if state.shape == sparse_operator.shape:
        product = state * sparse_operator
        expectation = numpy.sum(product.diagonal())

    elif state.shape == (sparse_operator.shape[0], 1):
        # Handle state vector.
        expectation = state.getH() * sparse_operator * state
        expectation = expectation[0, 0]

    else:
        # Handle exception.
        raise ValueError('Input state has invalid format.')

    # Return.
    return expectation


def expectation_computational_basis_state(operator, computational_basis_state):
    """Compute expectation value of operator with a  state.

    Args:
        operator: Qubit or FermionOperator to evaluate expectation value of.
                  If operator is a FermionOperator, it must be normal-ordered.
        computational_basis_state (scipy.sparse vector / list): normalized
            computational basis state (if scipy.sparse vector), or list of
            occupied orbitals.

    Returns:
        A real float giving expectation value.

    Raises:
        TypeError: Incorrect operator or state type.
    """
    if isinstance(operator, QubitOperator):
        raise NotImplementedError('Not yet implemented for QubitOperators.')

    if not isinstance(operator, FermionOperator):
        raise TypeError('operator must be a FermionOperator.')

    occupied_orbitals = computational_basis_state

    if not isinstance(occupied_orbitals, list):
        computational_basis_state_index = (
            occupied_orbitals.nonzero()[0][0])

        occupied_orbitals = [digit == '1' for digit in
                             bin(computational_basis_state_index)[2:]][::-1]

    expectation_value = operator.terms.get((), 0.0)

    for i in range(len(occupied_orbitals)):
        if occupied_orbitals[i]:
            expectation_value += operator.terms.get(
                ((i, 1), (i, 0)), 0.0)

            for j in range(i + 1, len(occupied_orbitals)):
                expectation_value -= operator.terms.get(
                    ((j, 1), (i, 1), (j, 0), (i, 0)), 0.0)

    return expectation_value


def expectation_db_operator_with_pw_basis_state(
        operator, plane_wave_occ_orbitals, n_spatial_orbitals, grid,
        spinless):
    """Compute expectation value of a dual basis operator with a plane
    wave computational basis state.

    Args:
        operator: Dual-basis representation of FermionOperator to evaluate
                  expectation value of. Can have at most 3-body terms.
        plane_wave_occ_orbitals (list): list of occupied plane-wave orbitals.
        n_spatial_orbitals (int): Number of spatial orbitals.
        grid (maya.utils.Grid): The grid used for discretization.
        spinless (bool): Whether the system is spinless.

    Returns:
        A real float giving the expectation value.
    """
    expectation_value = operator.terms.get((), 0.0)

    for single_action, coefficient in iteritems(operator.terms):
        if len(single_action) == 2:
            expectation_value += coefficient * (
                expectation_one_body_db_operator_computational_basis_state(
                    single_action, plane_wave_occ_orbitals, grid, spinless) /
                n_spatial_orbitals)

        elif len(single_action) == 4:
            expectation_value += coefficient * (
                expectation_two_body_db_operator_computational_basis_state(
                    single_action, plane_wave_occ_orbitals, grid, spinless) /
                n_spatial_orbitals ** 2)

        elif len(single_action) == 6:
            expectation_value += coefficient * (
                expectation_three_body_db_operator_computational_basis_state(
                    single_action, plane_wave_occ_orbitals, grid, spinless) /
                n_spatial_orbitals ** 3)

    return expectation_value


def expectation_one_body_db_operator_computational_basis_state(
        dual_basis_action, plane_wave_occ_orbitals, grid, spinless):
    """Compute expectation value of a 1-body dual-basis operator with a
    plane wave computational basis state.

    Args:
        dual_basis_action: Dual-basis action of FermionOperator to
                           evaluate expectation value of.
        plane_wave_occ_orbitals (list): list of occupied plane-wave orbitals.
        grid (maya.utils.Grid): The grid used for discretization.
        spinless (bool): Whether the system is spinless.

    Returns:
        A real float giving the expectation value.
    """
    expectation_value = 0.0

    r_p = position_vector(grid_indices(dual_basis_action[0][0],
                                       grid, spinless), grid)
    r_q = position_vector(grid_indices(dual_basis_action[1][0],
                                       grid, spinless), grid)

    for orbital in plane_wave_occ_orbitals:
        # If there's spin, p and q have to have the same parity (spin),
        # and the new orbital has to have the same spin as these.
        k_orbital = momentum_vector(grid_indices(orbital,
                                                 grid, spinless), grid)
        # The Fourier transform is spin-conserving. This means that p, q,
        # and the new orbital all have to have the same spin (parity).
        if spinless or (dual_basis_action[0][0] % 2 ==
                        dual_basis_action[1][0] % 2 == orbital % 2):
            expectation_value += numpy.exp(-1j * k_orbital.dot(r_p - r_q))

    return expectation_value


def expectation_two_body_db_operator_computational_basis_state(
        dual_basis_action, plane_wave_occ_orbitals, grid, spinless):
    """Compute expectation value of a 2-body dual-basis operator with a
    plane wave computational basis state.

    Args:
        dual_basis_action: Dual-basis action of FermionOperator to
                           evaluate expectation value of.
        plane_wave_occ_orbitals (list): list of occupied plane-wave orbitals.
        grid (maya.utils.Grid): The grid used for discretization.
        spinless (bool): Whether the system is spinless.

    Returns:
        A float giving the expectation value.
    """
    expectation_value = 0.0

    r_a = position_vector(grid_indices(dual_basis_action[0][0],
                                       grid, spinless), grid)
    r_b = position_vector(grid_indices(dual_basis_action[1][0],
                                       grid, spinless), grid)
    r_c = position_vector(grid_indices(dual_basis_action[2][0],
                                       grid, spinless), grid)
    r_d = position_vector(grid_indices(dual_basis_action[3][0],
                                       grid, spinless), grid)

    kac_dict = {}
    kad_dict = {}
    kbc_dict = {}
    kbd_dict = {}
    for i in plane_wave_occ_orbitals:
        k = momentum_vector(grid_indices(i, grid, spinless), grid)
        kac_dict[i] = k.dot(r_a - r_c)
        kad_dict[i] = k.dot(r_a - r_d)
        kbc_dict[i] = k.dot(r_b - r_c)
        kbd_dict[i] = k.dot(r_b - r_d)

    for orbital1 in plane_wave_occ_orbitals:
        k1ac = kac_dict[orbital1]
        k1ad = kad_dict[orbital1]

        for orbital2 in plane_wave_occ_orbitals:
            if orbital1 != orbital2:
                k2bc = kbc_dict[orbital2]
                k2bd = kbd_dict[orbital2]

                # The Fourier transform is spin-conserving. This means that
                # the parity of the orbitals involved in the transition must
                # be the same.
                if spinless or (
                        (dual_basis_action[0][0] % 2 ==
                         dual_basis_action[3][0] % 2 == orbital1 % 2) and
                        (dual_basis_action[1][0] % 2 ==
                         dual_basis_action[2][0] % 2 == orbital2 % 2)):
                    value = numpy.exp(-1j * (k1ad + k2bc))
                    # Add because it came from two anti-commutations.
                    expectation_value += value

                # The Fourier transform is spin-conserving. This means that
                # the parity of the orbitals involved in the transition must
                # be the same.
                if spinless or (
                        (dual_basis_action[0][0] % 2 ==
                         dual_basis_action[2][0] % 2 == orbital1 % 2) and
                        (dual_basis_action[1][0] % 2 ==
                         dual_basis_action[3][0] % 2 == orbital2 % 2)):
                    value = numpy.exp(-1j * (k1ac + k2bd))
                    # Subtract because it came from a single anti-commutation.
                    expectation_value -= value

    return expectation_value


def expectation_three_body_db_operator_computational_basis_state(
        dual_basis_action, plane_wave_occ_orbitals, grid, spinless):
    """Compute expectation value of a 3-body dual-basis operator with a
    plane wave computational basis state.

    Args:
        dual_basis_action: Dual-basis action of FermionOperator to
                           evaluate expectation value of.
        plane_wave_occ_orbitals (list): list of occupied plane-wave orbitals.
        grid (maya.utils.Grid): The grid used for discretization.
        spinless (bool): Whether the system is spinless.

    Returns:
        A float giving the expectation value.
    """
    expectation_value = 0.0

    r_a = position_vector(grid_indices(dual_basis_action[0][0],
                                       grid, spinless), grid)
    r_b = position_vector(grid_indices(dual_basis_action[1][0],
                                       grid, spinless), grid)
    r_c = position_vector(grid_indices(dual_basis_action[2][0],
                                       grid, spinless), grid)
    r_d = position_vector(grid_indices(dual_basis_action[3][0],
                                       grid, spinless), grid)
    r_e = position_vector(grid_indices(dual_basis_action[4][0],
                                       grid, spinless), grid)
    r_f = position_vector(grid_indices(dual_basis_action[5][0],
                                       grid, spinless), grid)

    kad_dict = {}
    kae_dict = {}
    kaf_dict = {}
    kbd_dict = {}
    kbe_dict = {}
    kbf_dict = {}
    kcd_dict = {}
    kce_dict = {}
    kcf_dict = {}
    for i in plane_wave_occ_orbitals:
        k = momentum_vector(grid_indices(i, grid, spinless), grid)
        kad_dict[i] = k.dot(r_a - r_d)
        kae_dict[i] = k.dot(r_a - r_e)
        kaf_dict[i] = k.dot(r_a - r_f)
        kbd_dict[i] = k.dot(r_b - r_d)
        kbe_dict[i] = k.dot(r_b - r_e)
        kbf_dict[i] = k.dot(r_b - r_f)
        kcd_dict[i] = k.dot(r_c - r_d)
        kce_dict[i] = k.dot(r_c - r_e)
        kcf_dict[i] = k.dot(r_c - r_f)

    for orbital1 in plane_wave_occ_orbitals:
        k1ad = kad_dict[orbital1]
        k1ae = kae_dict[orbital1]
        k1af = kaf_dict[orbital1]

        for orbital2 in plane_wave_occ_orbitals:
            if orbital1 != orbital2:
                k2bd = kbd_dict[orbital2]
                k2be = kbe_dict[orbital2]
                k2bf = kbf_dict[orbital2]

                for orbital3 in plane_wave_occ_orbitals:
                    if orbital1 != orbital3 and orbital2 != orbital3:
                        k3cd = kcd_dict[orbital3]
                        k3ce = kce_dict[orbital3]
                        k3cf = kcf_dict[orbital3]

                        # Handle \delta_{ad} \delta_{bf} \delta_{ce} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value += numpy.exp(-1j * (
                                k1ad + k2bf + k3ce))

                        # Handle -\delta_{ad} \delta_{be} \delta_{cf} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value -= numpy.exp(-1j * (
                                k1ad + k2be + k3cf))

                        # Handle -\delta_{ae} \delta_{bf} \delta_{cd} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value -= numpy.exp(-1j * (
                                k1ae + k2bf + k3cd))

                        # Handle \delta_{ae} \delta_{bd} \delta_{cf} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value += numpy.exp(-1j * (
                                k1ae + k2bd + k3cf))

                        # Handle \delta_{af} \delta_{be} \delta_{cd} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value += numpy.exp(-1j * (
                                k1af + k2be + k3cd))

                        # Handle -\delta_{af} \delta_{bd} \delta_{ce} after FT.
                        # The Fourier transform is spin-conserving.
                        if spinless or (
                                (dual_basis_action[0][0] % 2 ==
                                 dual_basis_action[5][0] % 2 ==
                                 orbital1 % 2) and
                                (dual_basis_action[1][0] % 2 ==
                                 dual_basis_action[3][0] % 2 ==
                                 orbital2 % 2) and
                                (dual_basis_action[2][0] % 2 ==
                                 dual_basis_action[4][0] % 2 ==
                                 orbital3 % 2)):
                            expectation_value -= numpy.exp(-1j * (
                                k1af + k2bd + k3ce))

    return expectation_value


def get_gap(sparse_operator):
    """Compute gap between lowest eigenvalue and first excited state.

    Returns: A real float giving eigenvalue gap.
    """
    if not is_hermitian(sparse_operator):
        raise ValueError('sparse_operator must be Hermitian.')

    values, _ = scipy.sparse.linalg.eigsh(
        sparse_operator, 2, which='SA', maxiter=1e7)

    gap = abs(values[1] - values[0])
    return gap