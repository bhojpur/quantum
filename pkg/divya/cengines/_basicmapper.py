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

"""
The parent class from which all mappers should be derived.

There is only one engine currently allowed to be derived from BasicMapperEngine. This allows the simulator to
automatically translate logical qubit ids to mapped ids.
"""
from copy import deepcopy

from divya.meta import LogicalQubitIDTag, drop_engine_after, insert_engine
from divya.ops import MeasureGate

from ._basics import BasicEngine
from ._cmdmodifier import CommandModifier

class BasicMapperEngine(BasicEngine):
    """
    Parent class for all Mappers.

    Attributes:
        self.current_mapping (dict): Keys are the logical qubit ids and values are the mapped qubit ids.

    """

    def __init__(self):
        """Initialize a BasicMapperEngine object."""
        super().__init__()
        self._current_mapping = None

    @property
    def current_mapping(self):
        """Access the current mapping."""
        return deepcopy(self._current_mapping)

    @current_mapping.setter
    def current_mapping(self, current_mapping):
        """Set the current mapping."""
        self._current_mapping = current_mapping

    def _send_cmd_with_mapped_ids(self, cmd):
        """
        Send this Command using the mapped qubit ids of self.current_mapping.

        If it is a Measurement gate, then it adds a LogicalQubitID tag.

        Args:
            cmd: Command object with logical qubit ids.
        """
        new_cmd = deepcopy(cmd)
        qubits = new_cmd.qubits
        for qureg in qubits:
            for qubit in qureg:
                if qubit.id != -1:
                    qubit.id = self.current_mapping[qubit.id]
        control_qubits = new_cmd.control_qubits
        for qubit in control_qubits:
            qubit.id = self.current_mapping[qubit.id]
        if isinstance(new_cmd.gate, MeasureGate):
            # Add LogicalQubitIDTag to MeasureGate
            def add_logical_id(command, old_tags=deepcopy(cmd.tags)):
                command.tags = old_tags + [LogicalQubitIDTag(cmd.qubits[0][0].id)]
                return command

            tagger_eng = CommandModifier(add_logical_id)
            insert_engine(self, tagger_eng)
            self.send([new_cmd])
            drop_engine_after(self)
        else:
            self.send([new_cmd])

    def receive(self, command_list):
        """
        Receive a list of commands.

        This implementation simply forwards all commands to the next compiler engine while adjusting the qubit IDs of
        measurement gates.
        """
        for cmd in command_list:
            self._send_cmd_with_mapped_ids(cmd)