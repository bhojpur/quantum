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

"""Class and functions to store interaction operators."""
from __future__ import absolute_import

import itertools

from maya.ops import InteractionTensor


class InteractionOperatorError(Exception):
    pass

class InteractionOperator(InteractionTensor):
    """Class for storing 'interaction operators' which are defined to be
    fermionic operators consisting of one-body and two-body terms which
    conserve particle number and spin. The most common examples of data that
    will use this structure are molecular Hamiltonians. In principle,
    everything stored in this class could also be represented using the more
    general FermionOperator class. However, this class is able to exploit
    specific properties of how fermions interact to enable more numerically
    efficient manipulation of the data. Note that the operators stored in this
    class take the form: constant + \sum_{p, q} h_[p, q] a^\dagger_p a_q +

        \sum_{p, q, r, s} h_[p, q, r, s] a^\dagger_p a^\dagger_q a_r a_s.

    Attributes:
        n_qubits: An int giving the number of qubits.
        constant: A constant term in the operator given as a float.
            For instance, the nuclear repulsion energy.
        one_body_tensor: The coefficients of the one-body terms (h[p, q]).
            This is an n_qubits x n_qubits numpy array of floats.
        two_body_tensor: The coefficients of the two-body terms
            (h[p, q, r, s]). This is an n_qubits x n_qubits x n_qubits x
            n_qubits numpy array of floats.
    """

    def __init__(self, constant, one_body_tensor, two_body_tensor):
        """
        Initialize the InteractionOperator class.

        Args:
            constant: A constant term in the operator given as a
                float. For instance, the nuclear repulsion energy.
            one_body_tensor: The coefficients of the one-body terms (h[p,q]).
               This is an n_qubits x n_qubits numpy array of floats.
            two_body_tensor: The coefficients of the two-body terms
                (h[p, q, r, s]). This is an n_qubits x n_qubits x n_qubits x
                n_qubits numpy array of floats.
        """
        # Make sure nonzero elements are only for normal ordered terms.
        super(InteractionOperator, self).__init__(constant, one_body_tensor,
                                                  two_body_tensor)

    def unique_iter(self, complex_valued=False):
        """
        Iterate all terms that are not in the same symmetry group.

        Four point symmetry:
            1. pq = qp.
            2. pqrs = srqp = qpsr = rspq.
        Eight point symmetry:
            1. pq = qp.
            2. pqrs = rqps = psrq = srqp = qpsr = rspq = spqr = qrsp.

        Args:
            complex_valued (bool):
                Whether the operator has complex coefficients.
        Yields:
            tuple[int]
        """
        # Constant.
        if self.constant:
            yield []

        # One-body terms.
        for p in range(self.n_qubits):
            for q in range(p + 1):
                if self.one_body_tensor[p, q]:
                    yield p, q

        # Two-body terms.
        seen = set()
        for quad in itertools.product(range(self.n_qubits), repeat=4):
            if self[quad] and quad not in seen:
                seen |= set(_symmetric_two_body_terms(quad, complex_valued))
                yield quad


def _symmetric_two_body_terms(quad, complex_valued):
    p, q, r, s = quad
    yield p, q, r, s
    yield q, p, s, r
    yield s, r, q, p
    yield r, s, p, q
    if not complex_valued:
        yield p, s, r, q
        yield q, r, s, p
        yield s, p, q, r
        yield r, q, p, s