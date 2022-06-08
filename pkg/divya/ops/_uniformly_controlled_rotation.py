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

"""Definition of uniformly controlled Ry- and Rz-rotation gates."""

import math

from ._basics import ANGLE_PRECISION, ANGLE_TOLERANCE, BasicGate, NotMergeable

class UniformlyControlledRy(BasicGate):
    """
    Uniformly controlled Ry gate as introduced in arXiv:quant-ph/0312218.

    This is an n-qubit gate. There are n-1 control qubits and one target qubit.  This gate applies Ry(angles(k)) to
    the target qubit if the n-1 control qubits are in the classical state k. As there are 2^(n-1) classical states for
    the control qubits, this gate requires 2^(n-1) (potentially different) angle parameters.

    Example:
        .. code-block:: python

        controls = eng.allocate_qureg(2)
        target = eng.allocate_qubit()
        UniformlyControlledRy(angles=[0.1, 0.2, 0.3, 0.4]) | (controls, target)

    Note:
        The first quantum register contains the control qubits. When converting the classical state k of the control
        qubits to an integer, we define controls[0] to be the least significant (qu)bit. controls can also be an empty
        list in which case the gate corresponds to an Ry.

    Args:
        angles(list[float]): Rotation angles. Ry(angles[k]) is applied conditioned on the control qubits being in
                             state k.
    """

    def __init__(self, angles):
        """Construct a UniformlyControlledRy gate."""
        super().__init__()
        rounded_angles = []
        for angle in angles:
            new_angle = round(float(angle) % (4.0 * math.pi), ANGLE_PRECISION)
            if new_angle > 4 * math.pi - ANGLE_TOLERANCE:
                new_angle = 0.0
            rounded_angles.append(new_angle)
        self.angles = rounded_angles

    def get_inverse(self):
        """Return the inverse of this rotation gate (negate the angles, return new object)."""
        return self.__class__([-1 * angle for angle in self.angles])

    def get_merged(self, other):
        """Return self merged with another gate."""
        if isinstance(other, self.__class__):
            new_angles = [angle1 + angle2 for (angle1, angle2) in zip(self.angles, other.angles)]
            return self.__class__(new_angles)
        raise NotMergeable()

    def __str__(self):
        """Return a string representation of the object."""
        return "UniformlyControlledRy(" + str(self.angles) + ")"

    def __eq__(self, other):
        """Return True if same class, same rotation angles."""
        if isinstance(other, self.__class__):
            return self.angles == other.angles
        return False

    def __hash__(self):
        """Compute the hash of the object."""
        return hash(str(self))

class UniformlyControlledRz(BasicGate):
    """
    Uniformly controlled Rz gate as introduced in arXiv:quant-ph/0312218.

    This is an n-qubit gate. There are n-1 control qubits and one target qubit.  This gate applies Rz(angles(k)) to
    the target qubit if the n-1 control qubits are in the classical state k. As there are 2^(n-1) classical states for
    the control qubits, this gate requires 2^(n-1) (potentially different) angle parameters.

    Example:
        .. code-block:: python

        controls = eng.allocate_qureg(2)
        target = eng.allocate_qubit()
        UniformlyControlledRz(angles=[0.1, 0.2, 0.3, 0.4]) | (controls, target)

    Note:
        The first quantum register are the contains qubits. When converting the classical state k of the control
        qubits to an integer, we define controls[0] to be the least significant (qu)bit. controls can also be an empty
        list in which case the gate corresponds to an Rz.

    Args:
        angles(list[float]): Rotation angles. Rz(angles[k]) is applied conditioned on the control qubits being in
                             state k.
    """

    def __init__(self, angles):
        """Construct a UniformlyControlledRz gate."""
        super().__init__()
        rounded_angles = []
        for angle in angles:
            new_angle = round(float(angle) % (4.0 * math.pi), ANGLE_PRECISION)
            if new_angle > 4 * math.pi - ANGLE_TOLERANCE:
                new_angle = 0.0
            rounded_angles.append(new_angle)
        self.angles = rounded_angles

    def get_inverse(self):
        """Return the inverse of this rotation gate (negate the angles, return new object)."""
        return self.__class__([-1 * angle for angle in self.angles])

    def get_merged(self, other):
        """Return self merged with another gate."""
        if isinstance(other, self.__class__):
            new_angles = [angle1 + angle2 for (angle1, angle2) in zip(self.angles, other.angles)]
            return self.__class__(new_angles)
        raise NotMergeable()

    def __str__(self):
        """Return a string representation of the object."""
        return "UniformlyControlledRz(" + str(self.angles) + ")"

    def __eq__(self, other):
        """Return True if same class, same rotation angles."""
        if isinstance(other, self.__class__):
            return self.angles == other.angles
        return False

    def __hash__(self):
        """Compute the hash of the object."""
        return hash(str(self))