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

"""Contains a compiler engine which prints commands to stdout prior to sending them on to the next engines."""

import sys
from builtins import input

from divya.cengines import BasicEngine, LastEngineException
from divya.meta import LogicalQubitIDTag, get_control_count
from divya.ops import FlushGate, Measure
from divya.types import WeakQubitRef

class CommandPrinter(BasicEngine):
    """
    Compiler engine that prints command to the standard output.

    CommandPrinter is a compiler engine which prints commands to stdout prior to sending them on to the next compiler
    engine.
    """

    def __init__(self, accept_input=True, default_measure=False, in_place=False):
        """
        Initialize a CommandPrinter.

        Args:
            accept_input (bool): If accept_input is true, the printer queries the user to input measurement results if
                the CommandPrinter is the last engine. Otherwise, all measurements yield default_measure.
            default_measure (bool): Default measurement result (if accept_input is False).
            in_place (bool): If in_place is true, all output is written on the same line of the terminal.
        """
        super().__init__()
        self._accept_input = accept_input
        self._default_measure = default_measure
        self._in_place = in_place

    def is_available(self, cmd):
        """
        Test whether a Command is supported by a compiler engine.

        Specialized implementation of is_available: Returns True if the CommandPrinter is the last engine (since it
        can print any command).

        Args:
            cmd (Command): Command of which to check availability (all Commands can be printed).
        Returns:
            availability (bool): True, unless the next engine cannot handle the Command (if there is a next engine).
        """
        try:
            return BasicEngine.is_available(self, cmd)
        except LastEngineException:
            return True

    def _print_cmd(self, cmd):
        """
        Print a command.

        Print a command or, if the command is a measurement instruction and the CommandPrinter is the last engine in
        the engine pipeline: Query the user for the measurement result (if accept_input = True) / Set the result to 0
        (if it's False).

        Args:
            cmd (Command): Command to print.
        """
        if self.is_last_engine and cmd.gate == Measure:
            if get_control_count(cmd) != 0:
                raise ValueError('Cannot have control qubits with a measurement gate!')

            print(cmd)
            for qureg in cmd.qubits:
                for qubit in qureg:
                    if self._accept_input:
                        meas = None
                        while meas not in ('0', '1', 1, 0):
                            prompt = "Input measurement result (0 or 1) for qubit " + str(qubit) + ": "
                            meas = input(prompt)
                    else:
                        meas = self._default_measure
                    meas = int(meas)
                    # Check there was a mapper and redirect result
                    logical_id_tag = None
                    for tag in cmd.tags:
                        if isinstance(tag, LogicalQubitIDTag):
                            logical_id_tag = tag
                    if logical_id_tag is not None:
                        qubit = WeakQubitRef(qubit.engine, logical_id_tag.logical_qubit_id)
                    self.main_engine.set_measurement_result(qubit, meas)
        else:
            if self._in_place:  # pragma: no cover
                sys.stdout.write("\0\r\t\x1b[K" + str(cmd) + "\r")
            else:
                print(cmd)

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a list of commands from the previous engine, print the
        commands, and then send them on to the next engine.

        Args:
            command_list (list<Command>): List of Commands to print (and
                potentially send on to the next engine).
        """
        for cmd in command_list:
            if not cmd.gate == FlushGate():
                self._print_cmd(cmd)
            # (try to) send on
            if not self.is_last_engine:
                self.send([cmd])