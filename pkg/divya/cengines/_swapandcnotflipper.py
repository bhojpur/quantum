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
A compiler engine which flips the directionality of CNOTs according to the given connectivity graph.

It also translates Swap gates to CNOTs if necessary.
"""
from copy import deepcopy

from divya.meta import get_control_count
from divya.ops import CNOT, NOT, All, H, Swap

from ._basics import BasicEngine, ForwarderEngine
from ._cmdmodifier import CommandModifier

class SwapAndCNOTFlipper(BasicEngine):
    """
    Flip CNOTs and translates Swaps to CNOTs where necessary.

    Warning:
        This engine assumes that CNOT and Hadamard gates are supported by the following engines.

    Warning:
        This engine cannot be used as a backend.
    """

    def __init__(self, connectivity):
        """
        Initialize the engine.

        Args:
            connectivity (set): Set of tuples (c, t) where if (c, t) is an element of the set means that a CNOT can be
                performed between the physical ids (c, t) with c being the control and t being the target qubit.
        """
        super().__init__()
        self.connectivity = connectivity

    def is_available(self, cmd):
        """
        Check if the IBM backend can perform the Command cmd and return True if so.

        Args:
            cmd (Command): The command to check
        """
        return self._is_swap(cmd) or self.next_engine.is_available(cmd)

    def _is_cnot(self, cmd):  # pylint: disable=no-self-use
        """
        Check if the command corresponds to a CNOT (controlled NOT gate).

        Args:
            cmd (Command): Command to check
        """
        return isinstance(cmd.gate, NOT.__class__) and get_control_count(cmd) == 1

    def _is_swap(self, cmd):  # pylint: disable=no-self-use
        """
        Check if the command corresponds to a Swap gate.

        Args:
            cmd (Command): Command to check
        """
        return get_control_count(cmd) == 0 and cmd.gate == Swap

    def _needs_flipping(self, cmd):
        """
        Return True if cmd is a CNOT which needs to be flipped around.

        Args:
            cmd (Command): Command to check
        """
        if not self._is_cnot(cmd):
            return False

        target = cmd.qubits[0][0].id
        control = cmd.control_qubits[0].id
        is_possible = (control, target) in self.connectivity
        if not is_possible and (target, control) not in self.connectivity:
            raise RuntimeError("The provided connectivity does not allow to execute the CNOT gate {}.".format(str(cmd)))
        return not is_possible

    def _send_cnot(self, cmd, control, target, flip=False):
        def cmd_mod(command):
            command.tags = deepcopy(cmd.tags) + command.tags
            command.engine = self.main_engine
            return command

        # We'll have to add all meta tags before sending on
        cmd_mod_eng = CommandModifier(cmd_mod)
        cmd_mod_eng.next_engine = self.next_engine
        cmd_mod_eng.main_engine = self.main_engine
        # forward everything to the command modifier
        forwarder_eng = ForwarderEngine(cmd_mod_eng)
        target[0].engine = forwarder_eng
        control[0].engine = forwarder_eng
        if flip:
            # flip the CNOT using Hadamard gates:
            All(H) | (control + target)
            CNOT | (target, control)
            All(H) | (control + target)
        else:
            CNOT | (control, target)

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a command list and if the command is a CNOT gate, it flips it using Hadamard gates if necessary; if it
        is a Swap gate, it decomposes it using 3 CNOTs. All other gates are simply sent to the next engine.

        Args:
            command_list (list of Command objects): list of commands to receive.
        """
        for cmd in command_list:
            if self._needs_flipping(cmd):
                self._send_cnot(cmd, cmd.control_qubits, cmd.qubits[0], True)
            elif self._is_swap(cmd):
                qubits = [qb for qr in cmd.qubits for qb in qr]
                ids = [qb.id for qb in qubits]
                if len(ids) != 2:
                    raise RuntimeError('Swap gate is a 2-qubit gate!')
                if tuple(ids) in self.connectivity:
                    control = [qubits[0]]
                    target = [qubits[1]]
                elif tuple(reversed(ids)) in self.connectivity:
                    control = [qubits[1]]
                    target = [qubits[0]]
                else:
                    raise RuntimeError(
                        "The provided connectivity does not allow to execute the Swap gate {}.".format(str(cmd))
                    )
                self._send_cnot(cmd, control, target)
                self._send_cnot(cmd, target, control, True)
                self._send_cnot(cmd, control, target)
            else:
                self.next_engine.receive([cmd])