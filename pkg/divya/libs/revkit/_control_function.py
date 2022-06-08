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

"""RevKit support for control function oracles."""

from divya.ops import BasicGate

from ._utils import _exec

class ControlFunctionOracle:  # pylint: disable=too-few-public-methods
    """
    Synthesize a negation controlled by an arbitrary control function.

    This creates a circuit for a NOT gate which is controlled by an arbitrary
    Boolean control function.  The control function is provided as integer
    representation of the function's truth table in binary notation.  For
    example, for the majority-of-three function, which truth table 11101000,
    the value for function can be, e.g., ``0b11101000``, ``0xe8``, or ``232``.

    Example:
        This example creates a circuit that causes to invert qubit ``d``,
        the majority-of-three function evaluates to true for the control
        qubits ``a``, ``b``, and ``c``.

        .. code-block:: python

            ControlFunctionOracle(0x8e) | ([a, b, c], d)
    """

    def __init__(self, function, **kwargs):
        """
        Initialize a control function oracle.

        Args:
            function (int): Function truth table.

        Keyword Args:
            synth: A RevKit synthesis command which creates a reversible
                   circuit based on a truth table and requires no additional
                   ancillae (e.g., ``revkit.esopbs``).  Can also be a nullary
                   lambda that calls several RevKit commands.
                   **Default:** ``revkit.esopbs``
        """
        if isinstance(function, int):
            self.function = function
        else:
            try:
                import dormouse  # pylint: disable=import-outside-toplevel

                self.function = dormouse.to_truth_table(function)
            except ImportError as err:  # pragma: no cover
                raise RuntimeError(
                    "The dormouse library needs to be installed in order to "
                    "automatically compile Python code into functions.  Try "
                    "to install dormouse with 'pip install dormouse'."
                ) from err
        self.kwargs = kwargs

        self._check_function()

    def __or__(self, qubits):
        """
        Apply control function to qubits (and synthesizes circuit).

        Args:
            qubits (tuple<Qureg>): Qubits to which the control function is
                                   being applied. The first `n` qubits are for
                                   the controls, the last qubit is for the
                                   target qubit.
        """
        try:
            import revkit  # pylint: disable=import-outside-toplevel
        except ImportError as err:  # pragma: no cover
            raise RuntimeError(
                "The RevKit Python library needs to be installed and in the "
                "PYTHONPATH in order to call this function"
            ) from err
        # pylint: disable=invalid-name

        # convert qubits to tuple
        qs = []
        for item in BasicGate.make_tuple_of_qureg(qubits):
            qs += item if isinstance(item, list) else [item]

        # function truth table cannot be larger than number of control qubits
        # allow
        if 2 ** (2 ** (len(qs) - 1)) <= self.function:
            raise AttributeError("Function truth table exceeds number of control qubits")

        # create truth table from function integer
        hex_length = max(2 ** (len(qs) - 1) // 4, 1)
        revkit.tt(table="{0:#0{1}x}".format(self.function, hex_length))

        # create reversible circuit from truth table
        self.kwargs.get("synth", revkit.esopbs)()

        # check whether circuit has correct signature
        if revkit.ps(mct=True, silent=True)['qubits'] != len(qs):
            raise RuntimeError("Generated circuit lines does not match provided qubits")

        # convert reversible circuit to Bhojpur Quantum code and execute it
        _exec(revkit.to_divya(mct=True), qs)

    def _check_function(self):
        """Check whether function is valid."""
        # function must be positive. We check in __or__ whether function is
        # too large
        if self.function < 0:
            raise AttributeError("Function must be a postive integer")