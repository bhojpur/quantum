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

"""Bravyi-Kitaev transform on fermionic operators."""
from __future__ import absolute_import

from maya.transforms._fenwick_tree import FenwickTree

from divya.ops import QubitOperator

def bravyi_kitaev(operator, n_qubits=None):
    """Apply the Bravyi-Kitaev transform and return qubit operator.

    Args:
        operator (maya.ops.FermionOperator):
            A FermionOperator to transform.
        n_qubits (int|None):
            Can force the number of qubits in the resulting operator above the
            number that appear in the input operator.

    Returns:
        transformed_operator: An instance of the QubitOperator class.

    Raises:
        ValueError: Invalid number of qubits specified.
    """
    # Compute the number of qubits.
    from maya.utils import count_qubits
    if n_qubits is None:
        n_qubits = count_qubits(operator)
    if n_qubits < count_qubits(operator):
        raise ValueError('Invalid number of qubits specified.')

    # Build the Fenwick tree.
    fenwick_tree = FenwickTree(n_qubits)

    # Compute transformed operator.
    transformed_terms = (
        _transform_operator_term(term=term,
                                 coefficient=operator.terms[term],
                                 fenwick_tree=fenwick_tree)
        for term in operator.terms
    )
    return inline_sum(seed=QubitOperator(), summands=transformed_terms)


def _transform_operator_term(term, coefficient, fenwick_tree):
    """
    Args:
        term (list[tuple[int, int]]):
            A list of (mode, raising-vs-lowering) ladder operator terms.
        coefficient (float):
        fenwick_tree (FenwickTree):
    Returns:
        QubitOperator:
    """

    # Build the Bravyi-Kitaev transformed operators.
    transformed_ladder_ops = (
        _transform_ladder_operator(ladder_operator, fenwick_tree)
        for ladder_operator in term
    )
    return inline_product(seed=QubitOperator((), coefficient),
                          factors=transformed_ladder_ops)


def _transform_ladder_operator(ladder_operator, fenwick_tree):
    """
    Args:
        ladder_operator (tuple[int, int]):
        fenwick_tree (FenwickTree):
    Returns:
        QubitOperator:
    """
    index = ladder_operator[0]

    # Parity set. Set of nodes to apply Z to.
    parity_set = [node.index for node in
                  fenwick_tree.get_parity_set(index)]

    # Update set. Set of ancestors to apply X to.
    ancestors = [node.index for node in
                 fenwick_tree.get_update_set(index)]

    # The C(j) set.
    ancestor_children = [node.index for node in
                         fenwick_tree.get_remainder_set(index)]

    # Switch between lowering/raising operators.
    d_coefficient = -.5j if ladder_operator[1] else .5j

    # The fermion lowering operator is given by
    # a = (c+id)/2 where c, d are the majoranas.
    d_majorana_component = QubitOperator(
        (((ladder_operator[0], 'Y'),) +
         tuple((index, 'Z') for index in ancestor_children) +
         tuple((index, 'X') for index in ancestors)),
        d_coefficient)

    c_majorana_component = QubitOperator(
        (((ladder_operator[0], 'X'),) +
         tuple((index, 'Z') for index in parity_set) +
         tuple((index, 'X') for index in ancestors)),
        0.5)

    return c_majorana_component + d_majorana_component


def inline_sum(seed, summands):
    """Computes a sum, using the __iadd__ operator.
    Args:
        seed (T): The starting total. The zero value.
        summands (iterable[T]): Values to add (with +=) into the total.
    Returns:
        T: The result of adding all the factors into the zero value.
    """
    for r in summands:
        seed += r
    return seed


def inline_product(seed, factors):
    """Computes a product, using the __imul__ operator.
    Args:
        seed (T): The starting total. The unit value.
        factors (iterable[T]): Values to multiply (with *=) into the total.
    Returns:
        T: The result of multiplying all the factors into the unit value.
    """
    for r in factors:
        seed *= r
    return seed