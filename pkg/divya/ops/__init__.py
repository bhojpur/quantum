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

"""Bhojpur Quantum module containing all basic gates (operations)"""

from ._basics import (
    BasicGate,
    BasicMathGate,
    BasicPhaseGate,
    BasicRotationGate,
    ClassicalInstructionGate,
    FastForwardingGate,
    MatrixGate,
    NotInvertible,
    NotMergeable,
    SelfInverseGate,
)
from ._command import Command, CtrlAll, IncompatibleControlState, apply_command
from ._gates import *
from ._metagates import (
    All,
    C,
    ControlledGate,
    DaggeredGate,
    Tensor,
    get_inverse,
    is_identity,
)
from ._qaagate import QAA
from ._qftgate import QFT, QFTGate
from ._qpegate import QPE
from ._qubit_operator import QubitOperator
from ._shortcuts import *
from ._state_prep import StatePreparation
from ._time_evolution import TimeEvolution
from ._uniformly_controlled_rotation import UniformlyControlledRy, UniformlyControlledRz