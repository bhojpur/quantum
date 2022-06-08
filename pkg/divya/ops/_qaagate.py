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

"""Definition of the quantum amplitude amplification gate."""

from ._basics import BasicGate

class QAA(BasicGate):
    """
    Quantum Aplitude Amplification gate.

    (Quick reference https://en.wikipedia.org/wiki/Amplitude_amplification.  Complete reference G. Brassard, P. Hoyer,
    M. Mosca, A. Tapp (2000) Quantum Amplitude Amplification and Estimation https://arxiv.org/abs/quant-ph/0005055)

    Quantum Amplitude Amplification (QAA) executes the algorithm, but not the final measurement required to obtain the
    marked state(s) with high probability. The starting state on wich the QAA algorithm is executed is the one
    resulting of aplying the Algorithm on the |0> state.

    Example:
        .. code-block:: python

           def func_algorithm(eng,system_qubits):
               All(H) | system_qubits

           def func_oracle(eng,system_qubits,qaa_ancilla):
               # This oracle selects the state |010> as the one marked
               with Compute(eng):
                  All(X) | system_qubits[0::2]
               with Control(eng, system_qubits):
                  X | qaa_ancilla
               Uncompute(eng)

           system_qubits = eng.allocate_qureg(3)
           # Prepare the qaa_ancilla qubit in the |-> state
           qaa_ancilla = eng.allocate_qubit()
           X | qaa_ancilla
           H | qaa_ancilla

           # Creates the initial state form the Algorithm
           func_algorithm(eng, system_qubits)
           # Apply Quantum Amplitude Amplification the correct number of times
           num_it = int(math.pi/4.*math.sqrt(1 << 3))
           with Loop(eng, num_it):
               QAA(func_algorithm, func_oracle) | (system_qubits, qaa_ancilla)

           All(Measure) | system_qubits

    Warning:
        No qubit allocation/deallocation may take place during the call to the defined Algorithm
        :code:`func_algorithm`

    Attributes:
        func_algorithm: Algorithm that initialite the state and to be used in the QAA algorithm
        func_oracle: The Oracle that marks the state(s) as "good"
        system_qubits: the system we are interested on
        qaa_ancilla: auxiliary qubit that helps to invert the amplitude of the "good" states

    """

    def __init__(self, algorithm, oracle):
        """Initialize a QAA object."""
        super().__init__()
        self.algorithm = algorithm
        self.oracle = oracle

    def __str__(self):
        """Return a string representation of the object."""
        return 'QAA(Algorithm = {0}, Oracle = {1})'.format(str(self.algorithm.__name__), str(self.oracle.__name__))