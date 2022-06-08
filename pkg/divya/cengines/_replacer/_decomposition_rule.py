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

"""Module containing the definition of a decomposition rule."""

from divya.ops import BasicGate

class ThisIsNotAGateClassError(TypeError):
    """Exception raised when a gate instance is encountered instead of a gate class in a decomposition rule."""

class DecompositionRule:  # pylint: disable=too-few-public-methods
    """A rule for breaking down specific gates into sequences of simpler gates."""

    def __init__(self, gate_class, gate_decomposer, gate_recognizer=lambda cmd: True):
        """
        Initialize a DecompositionRule object.

        Args:
            gate_class (type): The type of gate that this rule decomposes.

                The gate class is redundant information used to make lookups faster when iterating over a circuit and
                deciding "which rules apply to this gate?" again and again.

                Note that this parameter is a gate type, not a gate instance.  You supply gate_class=MyGate or
                gate_class=MyGate().__class__, not gate_class=MyGate().

            gate_decomposer (function[divya.ops.Command]): Function which, given the command to decompose, applies
                a sequence of gates corresponding to the high-level function of a gate of type gate_class.

            gate_recognizer (function[divya.ops.Command] : boolean): A predicate that determines if the
                decomposition applies to the given command (on top of the filtering by gate_class).

                For example, a decomposition rule may only to apply rotation gates that rotate by a specific angle.

                If no gate_recognizer is given, the decomposition applies to all gates matching the gate_class.
        """
        # Check for common gate_class type mistakes.
        if isinstance(gate_class, BasicGate):
            raise ThisIsNotAGateClassError(
                "gate_class is a gate instance instead of a type of BasicGate."
                "\nDid you pass in someGate instead of someGate.__class__?"
            )
        if gate_class == type.__class__:
            raise ThisIsNotAGateClassError(
                "gate_class is type.__class__ instead of a type of BasicGate."
                "\nDid you pass in GateType.__class__ instead of GateType?"
            )

        self.gate_class = gate_class
        self.gate_decomposer = gate_decomposer
        self.gate_recognizer = gate_recognizer