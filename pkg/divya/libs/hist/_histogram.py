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

"""Functions to plot a histogram of measured data."""

import matplotlib.pyplot as plt

from divya.backends import Simulator

def histogram(backend, qureg):
    """
    Make a measurement outcome probability histogram for the given qubits.

    Args:
        backend (BasicEngine): A Bhojpur Quantum backend
        qureg (list of qubits and/or quregs): The qubits,
            for which to make the histogram

    Returns:
        A tuple (fig, axes, probabilities), where:
        fig: The histogram as figure
        axes: The axes of the histogram
        probabilities (dict): A dictionary mapping outcomes as string
            to their probabilities

    Note:
        Don't forget to call eng.flush() before using this function.
    """
    qubit_list = []
    for qb in qureg:
        if isinstance(qb, list):
            qubit_list.extend(qb)
        else:
            qubit_list.append(qb)

    if len(qubit_list) > 5:
        print('Warning: For {0} qubits there are 2^{0} different outcomes'.format(len(qubit_list)))
        print("The resulting histogram may look bad and/or take too long.")
        print("Consider calling histogram() with a sublist of the qubits.")

    if hasattr(backend, 'get_probabilities'):
        probabilities = backend.get_probabilities(qureg)
    elif isinstance(backend, Simulator):
        outcome = [0] * len(qubit_list)
        n_outcomes = 1 << len(qubit_list)
        probabilities = {}
        for i in range(n_outcomes):
            for pos in range(len(qubit_list)):
                if (1 << pos) & i:
                    outcome[pos] = 1
                else:
                    outcome[pos] = 0
            probabilities[''.join([str(bit) for bit in outcome])] = backend.get_probability(outcome, qubit_list)
    else:
        raise RuntimeError('Unable to retrieve probabilities from backend')

    # Empirical figure size for up to 5 qubits
    fig, axes = plt.subplots(figsize=(min(21.2, 2 + 0.6 * (1 << len(qubit_list))), 7))
    names = list(probabilities.keys())
    values = list(probabilities.values())
    axes.bar(names, values)
    fig.suptitle('Measurement Probabilities')
    return (fig, axes, probabilities)