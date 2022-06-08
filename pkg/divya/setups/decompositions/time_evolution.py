# -*- coding: utf-8 -*-

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

"""
Register decomposition for the TimeEvolution gates.

An exact straight forward decomposition of a TimeEvolution gate is possible
if the hamiltonian has only one term or if all the terms commute with each
other in which case one can implement each term individually.
"""
import math

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, Uncompute
from divya.ops import CNOT, H, QubitOperator, Rx, Ry, Rz, TimeEvolution

def _recognize_time_evolution_commuting_terms(cmd):
    """Recognize all TimeEvolution gates with >1 terms but which all commute."""
    hamiltonian = cmd.gate.hamiltonian
    if len(hamiltonian.terms) == 1:
        return False
    id_op = QubitOperator((), 0.0)
    for term in hamiltonian.terms:
        test_op = QubitOperator(term, hamiltonian.terms[term])
        for other in hamiltonian.terms:
            other_op = QubitOperator(other, hamiltonian.terms[other])
            commutator = test_op * other_op - other_op * test_op
            if not commutator.isclose(id_op, rel_tol=1e-9, abs_tol=1e-9):
                return False
    return True

def _decompose_time_evolution_commuting_terms(cmd):
    qureg = cmd.qubits
    eng = cmd.engine
    hamiltonian = cmd.gate.hamiltonian
    time = cmd.gate.time
    with Control(eng, cmd.control_qubits):
        for term in hamiltonian.terms:
            ind_operator = QubitOperator(term, hamiltonian.terms[term])
            TimeEvolution(time, ind_operator) | qureg

def _recognize_time_evolution_individual_terms(cmd):
    return len(cmd.gate.hamiltonian.terms) == 1

def _decompose_time_evolution_individual_terms(cmd):  # pylint: disable=too-many-branches
    """
    Implement a TimeEvolution gate with a hamiltonian having only one term.

    To implement exp(-i * t * hamiltonian), where the hamiltonian is only one
    term, e.g., hamiltonian = X0 x Y1 X Z2, we first perform local
    transformations to in order that all Pauli operators in the hamiltonian
    are Z. We then implement  exp(-i * t * (Z1 x Z2 x Z3) and transform the
    basis back to the original. For more details see, e.g.,

    James D. Whitfield, Jacob Biamonte & Aspuru-Guzik
    Simulation of electronic structure Hamiltonians using quantum computers,
    Molecular Physics, 109:5, 735-750 (2011).

    or

    Nielsen and Chuang, Quantum Computation and Information.
    """
    if len(cmd.qubits) != 1:
        raise ValueError('TimeEvolution gate can only accept a single quantum register')
    qureg = cmd.qubits[0]
    eng = cmd.engine
    time = cmd.gate.time
    hamiltonian = cmd.gate.hamiltonian
    if len(hamiltonian.terms) != 1:
        raise ValueError('This decomposition function only accepts single-term hamiltonians!')
    term = list(hamiltonian.terms)[0]
    coefficient = hamiltonian.terms[term]
    check_indices = set()

    # Check that hamiltonian is not identity term,
    # Previous __or__ operator should have apply a global phase instead:
    if term == ():
        raise ValueError('This decomposition function cannot accept a hamiltonian with an empty term!')

    # hamiltonian has only a single local operator
    if len(term) == 1:
        with Control(eng, cmd.control_qubits):
            if term[0][1] == 'X':
                Rx(time * coefficient * 2.0) | qureg[term[0][0]]
            elif term[0][1] == 'Y':
                Ry(time * coefficient * 2.0) | qureg[term[0][0]]
            else:
                Rz(time * coefficient * 2.0) | qureg[term[0][0]]
    # hamiltonian has more than one local operator
    else:
        with Control(eng, cmd.control_qubits):
            with Compute(eng):
                # Apply local basis rotations
                for index, action in term:
                    check_indices.add(index)
                    if action == 'X':
                        H | qureg[index]
                    elif action == 'Y':
                        Rx(math.pi / 2.0) | qureg[index]
                print(check_indices, set(range(len(qureg))))
                # Check that qureg had exactly as many qubits as indices:
                if check_indices != set(range(len(qureg))):
                    raise ValueError('Indices mismatch between hamiltonian terms and qubits')
                # Compute parity
                for i in range(len(qureg) - 1):
                    CNOT | (qureg[i], qureg[i + 1])
            Rz(time * coefficient * 2.0) | qureg[-1]
            # Uncompute parity and basis change
            Uncompute(eng)

rule_commuting_terms = DecompositionRule(
    gate_class=TimeEvolution,
    gate_decomposer=_decompose_time_evolution_commuting_terms,
    gate_recognizer=_recognize_time_evolution_commuting_terms,
)

rule_individual_terms = DecompositionRule(
    gate_class=TimeEvolution,
    gate_decomposer=_decompose_time_evolution_individual_terms,
    gate_recognizer=_recognize_time_evolution_individual_terms,
)

#: Decomposition rules
all_defined_decomposition_rules = [rule_commuting_terms, rule_individual_terms]