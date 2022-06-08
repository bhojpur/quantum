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

"""Mapper that has a maximum number of allocatable qubits."""

from divya.cengines import BasicMapperEngine
from divya.meta import LogicalQubitIDTag
from divya.ops import AllocateQubitGate, Command, DeallocateQubitGate, FlushGate
from divya.types import WeakQubitRef

class BoundedQubitMapper(BasicMapperEngine):
    """Map logical qubits to a fixed number of hardware qubits."""

    def __init__(self, max_qubits):
        """Initialize a BoundedQubitMapper object."""
        super().__init__()
        self._qubit_idx = 0
        self.max_qubits = max_qubits

    def _reset(self):
        # Reset the mapping index.
        self._qubit_idx = 0

    def _process_cmd(self, cmd):
        current_mapping = self.current_mapping
        if current_mapping is None:
            current_mapping = {}

        if isinstance(cmd.gate, AllocateQubitGate):
            qubit_id = cmd.qubits[0][0].id
            if qubit_id in current_mapping:
                raise RuntimeError("Qubit with id {} has already been allocated!".format(qubit_id))

            if self._qubit_idx >= self.max_qubits:
                raise RuntimeError("Cannot allocate more than {} qubits!".format(self.max_qubits))

            new_id = self._qubit_idx
            self._qubit_idx += 1
            current_mapping[qubit_id] = new_id
            qb = WeakQubitRef(engine=self, idx=new_id)
            new_cmd = Command(
                engine=self,
                gate=AllocateQubitGate(),
                qubits=([qb],),
                tags=[LogicalQubitIDTag(qubit_id)],
            )
            self.current_mapping = current_mapping
            self.send([new_cmd])
        elif isinstance(cmd.gate, DeallocateQubitGate):
            qubit_id = cmd.qubits[0][0].id
            if qubit_id not in current_mapping:
                raise RuntimeError("Cannot deallocate a qubit that is not already allocated!")
            qb = WeakQubitRef(engine=self, idx=current_mapping[qubit_id])
            new_cmd = Command(
                engine=self,
                gate=DeallocateQubitGate(),
                qubits=([qb],),
                tags=[LogicalQubitIDTag(qubit_id)],
            )
            current_mapping.pop(qubit_id)
            self.current_mapping = current_mapping
            self.send([new_cmd])
        else:
            self._send_cmd_with_mapped_ids(cmd)

    def receive(self, command_list):
        """
        Receive a list of commands.

        Args:
            command_list (list<Command>): List of commands to receive.
        """
        for cmd in command_list:
            if isinstance(cmd.gate, FlushGate):
                self._reset()
                self.send([cmd])
            else:
                self._process_cmd(cmd)

__all__ = ['BoundedQubitMapper']