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

"""RevKit support for permutation oracles."""

from divya.ops import BasicGate

from ._utils import _exec

class PermutationOracle:  # pylint: disable=too-few-public-methods
    """
    Synthesize a permutation using RevKit.

    Given a permutation over `2**q` elements (starting from 0), this class
    helps to automatically find a reversible circuit over `q` qubits that
    realizes that permutation.

    Example:
        .. code-block:: python

            PermutationOracle([0, 2, 1, 3]) | (a, b)
    """

    def __init__(self, permutation, **kwargs):
        """
        Initialize a permutation oracle.

        Args:
            permutation (list<int>): Permutation (starting from 0).

        Keyword Args:
            synth: A RevKit synthesis command which creates a reversible circuit based on a reversible truth table
                   (e.g., ``revkit.tbs`` or ``revkit.dbs``).  Can also be a nullary lambda that calls several RevKit
                   commands.
                   **Default:** ``revkit.tbs``
        """
        self.permutation = permutation
        self.kwargs = kwargs

        self._check_permutation()

    def __or__(self, qubits):
        """
        Apply permutation to qubits (and synthesizes circuit).

        Args:
            qubits (tuple<Qureg>): Qubits to which the permutation is being applied.
        """
        try:
            import revkit  # pylint: disable=import-outside-toplevel
        except ImportError as err:  # pragma: no cover
            raise RuntimeError(
                "The RevKit Python library needs to be installed and in the "
                "PYTHONPATH in order to call this function"
            ) from err

        # pylint: disable=invalid-name
        # convert qubits to flattened list
        qs = BasicGate.make_tuple_of_qureg(qubits)
        qs = sum(qs, [])

        # permutation must have 2*q elements, where q is the number of qubits
        if 2 ** (len(qs)) != len(self.permutation):
            raise AttributeError("Number of qubits does not fit to the size of the permutation")

        # create reversible truth table from permutation
        revkit.perm(permutation=" ".join(map(str, self.permutation)))

        # create reversible circuit from reversible truth table
        self.kwargs.get("synth", revkit.tbs)()

        # convert reversible circuit to Bhojpur Quantum code and execute it
        _exec(revkit.to_divya(mct=True), qs)

    def _check_permutation(self):
        """Check whether permutation is valid."""
        # permutation must start from 0, has no duplicates and all elements are
        # consecutive
        if sorted(set(self.permutation)) != list(range(len(self.permutation))):
            raise AttributeError("Invalid permutation (does it start from 0?)")