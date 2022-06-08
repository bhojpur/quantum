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

"""Tests for interaction_operators.py."""
from __future__ import absolute_import

import numpy
import unittest

from maya.ops import InteractionOperator


class InteractionOperatorsTest(unittest.TestCase):

    def setUp(self):
        self.n_qubits = 5
        self.constant = 0.
        self.one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        self.two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                     self.n_qubits, self.n_qubits), float)
        self.interaction_operator = InteractionOperator(self.constant,
                                                        self.one_body,
                                                        self.two_body)

    def test_four_point_iter(self):
        constant = 100.0
        one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                self.n_qubits, self.n_qubits), float)
        one_body[1, 1] = 10.0
        one_body[2, 3] = 11.0
        one_body[3, 2] = 11.0
        two_body[1, 2, 3, 4] = 12.0
        two_body[2, 1, 4, 3] = 12.0
        two_body[3, 4, 1, 2] = 12.0
        two_body[4, 3, 2, 1] = 12.0
        interaction_operator = InteractionOperator(
            constant, one_body, two_body)

        want_str = '100.0\n10.0\n11.0\n12.0\n'
        got_str = ''
        for key in interaction_operator.unique_iter(complex_valued=True):
            got_str += '{}\n'.format(interaction_operator[key])
        self.assertEqual(want_str, got_str)

    def test_eight_point_iter(self):
        constant = 100.0
        one_body = numpy.zeros((self.n_qubits, self.n_qubits), float)
        two_body = numpy.zeros((self.n_qubits, self.n_qubits,
                                self.n_qubits, self.n_qubits), float)
        one_body[1, 1] = 10.0
        one_body[2, 3] = 11.0
        one_body[3, 2] = 11.0
        two_body[1, 2, 3, 4] = 12.0
        two_body[2, 1, 4, 3] = 12.0
        two_body[3, 4, 1, 2] = 12.0
        two_body[4, 3, 2, 1] = 12.0
        two_body[1, 4, 3, 2] = 12.0
        two_body[2, 3, 4, 1] = 12.0
        two_body[3, 2, 1, 4] = 12.0
        two_body[4, 1, 2, 3] = 12.0
        interaction_operator = InteractionOperator(
            constant, one_body, two_body)

        want_str = '100.0\n10.0\n11.0\n12.0\n'
        got_str = ''
        for key in interaction_operator.unique_iter():
            got_str += '{}\n'.format(interaction_operator[key])
        self.assertEqual(want_str, got_str)