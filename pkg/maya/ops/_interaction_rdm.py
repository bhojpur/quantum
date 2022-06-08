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

"""Class and functions to store reduced density matrices."""
from __future__ import absolute_import

import copy
import numpy

from maya.ops import (FermionOperator,
                          InteractionTensor,
                          InteractionOperator,
                          normal_ordered)

from divya.ops import QubitOperator


class InteractionRDMError(Exception):
    pass


class InteractionRDM(InteractionTensor):
    """Class for storing 1- and 2-body reduced density matrices.

    Attributes:
        one_body_tensor: The expectation values <a^\dagger_p a_q>.
        two_body_tensor: The expectation values
            <a^\dagger_p a^\dagger_q a_r a_s>.
    """

    def __init__(self, one_body_tensor, two_body_tensor):
        """Initialize the InteractionRDM class.

        Args:
            one_body_tensor: Expectation values <a^\dagger_p a_q>.
            two_body_tensor: Expectation values
                <a^\dagger_p a^\dagger_q a_r a_s>.
        """
        super(InteractionRDM, self).__init__(None, one_body_tensor,
                                             two_body_tensor)

    @classmethod
    def from_spatial_rdm(cls, one_rdm_a, one_rdm_b,
                         two_rdm_aa, two_rdm_ab, two_rdm_bb):
        one_rdm, two_rdm = unpack_spatial_rdm(one_rdm_a, one_rdm_b,
                                              two_rdm_aa, two_rdm_ab,
                                              two_rdm_bb)
        return cls(constant, one_rdm, two_rdm)

    def expectation(self, operator):
        """Return expectation value of an InteractionRDM with an operator.

        Args:
            operator: A QubitOperator or InteractionOperator.

        Returns:
            float: Expectation value

        Raises:
            InteractionRDMError: Invalid operator provided.
        """
        if isinstance(operator, QubitOperator):
            expectation_op = self.get_qubit_expectations(operator)
            expectation = 0.0
            for qubit_term in operator.terms:
                expectation += (operator.terms[qubit_term] *
                                expectation_op.terms[qubit_term])
        elif isinstance(operator, InteractionOperator):
            expectation = operator.constant
            expectation += numpy.sum(self.one_body_tensor *
                                     operator.one_body_tensor)
            expectation += numpy.sum(self.two_body_tensor *
                                     operator.two_body_tensor)
        else:
            raise InteractionRDMError('Invalid operator type provided.')
        return expectation

    def get_qubit_expectations(self, qubit_operator):
        """Return expectations of QubitOperator in new QubitOperator.

        Args:
            qubit_operator: QubitOperator instance to be evaluated on
                this InteractionRDM.

        Returns:
            QubitOperator: QubitOperator with coefficients
            corresponding to expectation values of those operators.

        Raises:
            InteractionRDMError: Observable not contained in 1-RDM or 2-RDM.
        """
        from maya.transforms import reverse_jordan_wigner
        qubit_operator_expectations = copy.deepcopy(qubit_operator)
        for qubit_term in qubit_operator_expectations.terms:
            expectation = 0.

            # Map qubits back to fermions.
            reversed_fermion_operators = reverse_jordan_wigner(
                QubitOperator(qubit_term))
            reversed_fermion_operators = normal_ordered(
                reversed_fermion_operators)

            # Loop through fermion terms.
            for fermion_term in reversed_fermion_operators.terms:
                coefficient = reversed_fermion_operators.terms[fermion_term]

                # Handle molecular term.
                if FermionOperator(fermion_term).is_molecular_term():
                    if not fermion_term:
                        expectation += coefficient
                    else:
                        indices = [operator[0] for operator in fermion_term]
                        rdm_element = self[indices]
                        expectation += rdm_element * coefficient

                # Handle non-molecular terms.
                elif len(fermion_term) > 4:
                    raise InteractionRDMError('Observable not contained '
                                              'in 1-RDM or 2-RDM.')
            qubit_operator_expectations.terms[qubit_term] = expectation
        return qubit_operator_expectations