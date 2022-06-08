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

"""Register decomposition for StatePreparation."""

import cmath
import math

from divya.cengines import DecompositionRule
from divya.meta import Control, Dagger
from divya.ops import (
    Ph,
    StatePreparation,
    UniformlyControlledRy,
    UniformlyControlledRz,
)

def _decompose_state_preparation(cmd):  # pylint: disable=too-many-locals
    """Implement state preparation based on arXiv:quant-ph/0407010v1."""
    eng = cmd.engine
    if len(cmd.qubits) != 1:
        raise ValueError('StatePreparation does not support multiple quantum registers!')
    num_qubits = len(cmd.qubits[0])
    qureg = cmd.qubits[0]
    final_state = cmd.gate.final_state
    if len(final_state) != 2**num_qubits:
        raise ValueError("Length of final_state is invalid.")
    norm = 0.0
    for amplitude in final_state:
        norm += abs(amplitude) ** 2
    if norm < 1 - 1e-10 or norm > 1 + 1e-10:
        raise ValueError("final_state is not normalized.")
    with Control(eng, cmd.control_qubits):
        # As in the paper reference, we implement the inverse:
        with Dagger(eng):
            # Cancel all the relative phases
            phase_of_blocks = []
            for amplitude in final_state:
                phase_of_blocks.append(cmath.phase(amplitude))
            for qubit_idx, qubit in enumerate(qureg):
                angles = []
                phase_of_next_blocks = []
                for block in range(2 ** (len(qureg) - qubit_idx - 1)):
                    phase0 = phase_of_blocks[2 * block]
                    phase1 = phase_of_blocks[2 * block + 1]
                    angles.append(phase0 - phase1)
                    phase_of_next_blocks.append((phase0 + phase1) / 2.0)
                UniformlyControlledRz(angles) | (
                    qureg[(qubit_idx + 1) :],  # noqa: E203
                    qubit,
                )
                phase_of_blocks = phase_of_next_blocks
            # Cancel global phase
            Ph(-phase_of_blocks[0]) | qureg[-1]
            # Remove amplitudes from states which contain a bit value 1:
            abs_of_blocks = []
            for amplitude in final_state:
                abs_of_blocks.append(abs(amplitude))
            for qubit_idx, qubit in enumerate(qureg):
                angles = []
                abs_of_next_blocks = []
                for block in range(2 ** (len(qureg) - qubit_idx - 1)):
                    a0 = abs_of_blocks[2 * block]  # pylint: disable=invalid-name
                    a1 = abs_of_blocks[2 * block + 1]  # pylint: disable=invalid-name
                    if a0 == 0 and a1 == 0:
                        angles.append(0)
                    else:
                        angles.append(-2.0 * math.acos(a0 / math.sqrt(a0**2 + a1**2)))
                    abs_of_next_blocks.append(math.sqrt(a0**2 + a1**2))
                UniformlyControlledRy(angles) | (
                    qureg[(qubit_idx + 1) :],  # noqa: E203
                    qubit,
                )
                abs_of_blocks = abs_of_next_blocks

#: Decomposition rules
all_defined_decomposition_rules = [DecompositionRule(StatePreparation, _decompose_state_preparation)]