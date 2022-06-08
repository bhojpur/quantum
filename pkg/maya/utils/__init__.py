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

from ._chemical_series import (make_atomic_ring,
                               make_atomic_lattice,
                               make_atom)

from ._grid import Grid

from ._hubbard import fermi_hubbard

from ._jellium import (dual_basis_kinetic,
                       dual_basis_potential,
                       dual_basis_jellium_model,
                       jellium_model,
                       jordan_wigner_dual_basis_jellium,
                       plane_wave_kinetic,
                       plane_wave_potential)

from ._dual_basis_trotter_error import (dual_basis_error_bound,
                                        dual_basis_error_operator)

from ._molecular_data import MolecularData, periodic_table

from ._operator_utils import (commutator, count_qubits,
                              eigenspectrum, get_file_path, is_identity,
                              load_operator, save_operator)

from ._plane_wave_hamiltonian import (dual_basis_external_potential,
                                      fourier_transform,
                                      inverse_fourier_transform,
                                      plane_wave_external_potential,
                                      plane_wave_hamiltonian,
                                      jordan_wigner_dual_basis_hamiltonian,
                                      wigner_seitz_length_scale)

from ._sparse_tools import (expectation,
                            expectation_computational_basis_state,
                            get_density_matrix,
                            get_gap,
                            get_ground_state,
                            is_hermitian,
                            jordan_wigner_sparse,
                            jw_hartree_fock_state,
                            qubit_operator_sparse,
                            sparse_eigenspectrum)

from ._trotter_error import error_bound, error_operator