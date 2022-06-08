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

"""Register decomposition for UnformlyControlledRy and UnformlyControlledRz."""

from divya.cengines import DecompositionRule
from divya.meta import Compute, Control, CustomUncompute
from divya.ops import CNOT, Ry, Rz, UniformlyControlledRy, UniformlyControlledRz

def _apply_ucr_n(
    angles, ucontrol_qubits, target_qubit, eng, gate_class, rightmost_cnot
):  # pylint: disable=too-many-arguments
    if len(ucontrol_qubits) == 0:
        gate = gate_class(angles[0])
        if gate != gate_class(0):
            gate | target_qubit
    else:
        if rightmost_cnot[len(ucontrol_qubits)]:
            angles1 = []
            angles2 = []
            for lower_bits in range(2 ** (len(ucontrol_qubits) - 1)):
                leading_0 = angles[lower_bits]
                leading_1 = angles[lower_bits + 2 ** (len(ucontrol_qubits) - 1)]
                angles1.append((leading_0 + leading_1) / 2.0)
                angles2.append((leading_0 - leading_1) / 2.0)
        else:
            angles1 = []
            angles2 = []
            for lower_bits in range(2 ** (len(ucontrol_qubits) - 1)):
                leading_0 = angles[lower_bits]
                leading_1 = angles[lower_bits + 2 ** (len(ucontrol_qubits) - 1)]
                angles1.append((leading_0 - leading_1) / 2.0)
                angles2.append((leading_0 + leading_1) / 2.0)
        _apply_ucr_n(
            angles=angles1,
            ucontrol_qubits=ucontrol_qubits[:-1],
            target_qubit=target_qubit,
            eng=eng,
            gate_class=gate_class,
            rightmost_cnot=rightmost_cnot,
        )
        # Very custom usage of Compute/CustomUncompute in the following.
        if rightmost_cnot[len(ucontrol_qubits)]:
            with Compute(eng):
                CNOT | (ucontrol_qubits[-1], target_qubit)
        else:
            with CustomUncompute(eng):
                CNOT | (ucontrol_qubits[-1], target_qubit)
        _apply_ucr_n(
            angles=angles2,
            ucontrol_qubits=ucontrol_qubits[:-1],
            target_qubit=target_qubit,
            eng=eng,
            gate_class=gate_class,
            rightmost_cnot=rightmost_cnot,
        )
        # Next iteration on this level do the other cnot placement
        rightmost_cnot[len(ucontrol_qubits)] = not rightmost_cnot[len(ucontrol_qubits)]


def _decompose_ucr(cmd, gate_class):
    """
    Decomposition for an uniformly controlled single qubit rotation gate.

    Follows decomposition in arXiv:quant-ph/0407010 section II and
    arXiv:quant-ph/0410066v2 Fig. 9a.

    For Ry and Rz it uses 2**len(ucontrol_qubits) CNOT and also
    2**len(ucontrol_qubits) single qubit rotations.

    Args:
        cmd: CommandObject to decompose.
        gate_class: Ry or Rz
    """
    eng = cmd.engine
    with Control(eng, cmd.control_qubits):
        if not (len(cmd.qubits) == 2 and len(cmd.qubits[1]) == 1):
            raise TypeError("Wrong number of qubits ")
        ucontrol_qubits = cmd.qubits[0]
        target_qubit = cmd.qubits[1]
        if not len(cmd.gate.angles) == 2 ** len(ucontrol_qubits):
            raise ValueError("Wrong len(angles).")
        if len(ucontrol_qubits) == 0:
            gate_class(cmd.gate.angles[0]) | target_qubit
            return
        angles1 = []
        angles2 = []
        for lower_bits in range(2 ** (len(ucontrol_qubits) - 1)):
            leading_0 = cmd.gate.angles[lower_bits]
            leading_1 = cmd.gate.angles[lower_bits + 2 ** (len(ucontrol_qubits) - 1)]
            angles1.append((leading_0 + leading_1) / 2.0)
            angles2.append((leading_0 - leading_1) / 2.0)
        rightmost_cnot = {}
        for i in range(len(ucontrol_qubits) + 1):
            rightmost_cnot[i] = True
        _apply_ucr_n(
            angles=angles1,
            ucontrol_qubits=ucontrol_qubits[:-1],
            target_qubit=target_qubit,
            eng=eng,
            gate_class=gate_class,
            rightmost_cnot=rightmost_cnot,
        )
        # Very custom usage of Compute/CustomUncompute in the following.
        with Compute(cmd.engine):
            CNOT | (ucontrol_qubits[-1], target_qubit)
        _apply_ucr_n(
            angles=angles2,
            ucontrol_qubits=ucontrol_qubits[:-1],
            target_qubit=target_qubit,
            eng=eng,
            gate_class=gate_class,
            rightmost_cnot=rightmost_cnot,
        )
        with CustomUncompute(eng):
            CNOT | (ucontrol_qubits[-1], target_qubit)


def _decompose_ucry(cmd):
    return _decompose_ucr(cmd, gate_class=Ry)


def _decompose_ucrz(cmd):
    return _decompose_ucr(cmd, gate_class=Rz)


#: Decomposition rules
all_defined_decomposition_rules = [
    DecompositionRule(UniformlyControlledRy, _decompose_ucry),
    DecompositionRule(UniformlyControlledRz, _decompose_ucrz),
]