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

"""Definition of the state preparation gate."""

from ._basics import BasicGate

class StatePreparation(BasicGate):
    """Gate for transforming qubits in state |0> to any desired quantum state."""

    def __init__(self, final_state):
        """
        Initialize a StatePreparation gate.

        Example:
            .. code-block:: python

                qureg = eng.allocate_qureg(2)
                StatePreparation([0.5, -0.5j, -0.5, 0.5]) | qureg

        Note:
            final_state[k] is taken to be the amplitude of the computational basis state whose string is equal to the
            binary representation of k.

        Args:
            final_state(list[complex]): wavefunction of the desired quantum state. len(final_state) must be
                                        2**len(qureg). Must be normalized!
        """
        super().__init__()
        self.final_state = list(final_state)

    def __str__(self):
        """Return a string representation of the object."""
        return "StatePreparation"

    def __eq__(self, other):
        """Equal operator."""
        if isinstance(other, self.__class__):
            return self.final_state == other.final_state
        return False

    def __hash__(self):
        """Compute the hash of the object."""
        return hash("StatePreparation(" + str(self.final_state) + ")")