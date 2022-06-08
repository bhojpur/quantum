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

"""TestEngine and DummyEngine."""

from copy import deepcopy

from divya.ops import FlushGate

from ._basics import BasicEngine

def _compare_cmds(cmd1, cmd2):
    """Compare two command objects."""
    cmd2 = deepcopy(cmd2)
    cmd2.engine = cmd1.engine
    return cmd1 == cmd2

class CompareEngine(BasicEngine):
    """
    Command list comparison compiler engine for testing purposes.

    CompareEngine is an engine which saves all commands. It is only intended for testing purposes. Two CompareEngine
    backends can be compared and return True if they contain the same commmands.
    """

    def __init__(self):
        """Initialize a CompareEngine object."""
        super().__init__()
        self._l = [[]]

    def is_available(self, cmd):
        """All commands are accepted by this compiler engine."""
        return True

    def cache_cmd(self, cmd):
        """Cache a command."""
        # are there qubit ids that haven't been added to the list?
        all_qubit_id_list = [qubit.id for qureg in cmd.all_qubits for qubit in qureg]
        maxidx = int(0)
        for qubit_id in all_qubit_id_list:
            maxidx = max(maxidx, qubit_id)

        # if so, increase size of list to account for these qubits
        add = maxidx + 1 - len(self._l)
        if add > 0:
            for _ in range(add):
                self._l += [[]]

        # add gate command to each of the qubits involved
        for qubit_id in all_qubit_id_list:
            self._l[qubit_id] += [cmd]

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a command list and, for each command, stores it inside the cache before sending it to the next
        compiler engine.

        Args:
            command_list (list of Command objects): list of commands to receive.
        """
        for cmd in command_list:
            if not cmd.gate == FlushGate():
                self.cache_cmd(cmd)
        if not self.is_last_engine:
            self.send(command_list)

    def __eq__(self, other):
        """Equal operator."""
        if not isinstance(other, CompareEngine) or len(self._l) != len(other._l):
            return False
        for i, _li in enumerate(self._l):
            if len(_li) != len(other._l[i]):
                return False
            for j, _lij in enumerate(_li):
                if not _compare_cmds(_lij, other._l[i][j]):
                    return False
        return True

    def __str__(self):
        """Return a string representation of the object."""
        string = ""
        for qubit_id, _l in enumerate(self._l):
            string += "Qubit {0} : ".format(qubit_id)
            for command in self._l[qubit_id]:
                string += str(command) + ", "
            string = string[:-2] + "\n"
        return string

class DummyEngine(BasicEngine):
    """
    DummyEngine used for testing.

    The DummyEngine forwards all commands directly to next engine.  If self.is_last_engine == True it just discards
    all gates.
    By setting save_commands == True all commands get saved as a list in self.received_commands. Elements are appended
    to this list so they are ordered according to when they are received.
    """

    def __init__(self, save_commands=False):
        """
        Initialize a DummyEngine.

        Args:
            save_commands (default = False): If True, commands are saved in
                                             self.received_commands.
        """
        super().__init__()
        self.save_commands = save_commands
        self.received_commands = []

    def is_available(self, cmd):
        """All commands are accepted by this compiler engine."""
        return True

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a command list and, for each command, stores it internally if requested before sending it to the next
        compiler engine.

        Args:
            command_list (list of Command objects): list of commands to receive.
        """
        if self.save_commands:
            self.received_commands.extend(command_list)
        if not self.is_last_engine:
            self.send(command_list)