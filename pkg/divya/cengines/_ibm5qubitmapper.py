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

"""Contains a compiler engine to map to the 5-qubit IBM chip."""

import itertools

from divya.backends import IBMBackend
from divya.meta import get_control_count
from divya.ops import NOT, Allocate, FlushGate

from ._basicmapper import BasicMapperEngine

class IBM5QubitMapper(BasicMapperEngine):
    """
    Mapper for the 5-qubit IBM backend.

    Maps a given circuit to the IBM Quantum Experience chip.

    Note:
        The mapper has to be run once on the entire circuit.

    Warning:
        If the provided circuit cannot be mapped to the hardware layout without performing Swaps, the mapping
        procedure **raises an Exception**.
    """

    def __init__(self, connections=None):
        """
        Initialize an IBM 5-qubit mapper compiler engine.

        Resets the mapping.
        """
        super().__init__()
        self.current_mapping = {}
        self._reset()
        self._cmds = []
        self._interactions = {}

        if connections is None:
            # general connectivity easier for testing functions
            self.connections = {
                (0, 1),
                (1, 0),
                (1, 2),
                (1, 3),
                (1, 4),
                (2, 1),
                (2, 3),
                (2, 4),
                (3, 1),
                (3, 4),
                (4, 3),
            }
        else:
            self.connections = connections

    def is_available(self, cmd):
        """
        Check if the IBM backend can perform the Command cmd and return True if so.

        Args:
            cmd (Command): The command to check
        """
        return IBMBackend().is_available(cmd)

    def _reset(self):
        """Reset the mapping parameters so the next circuit can be mapped."""
        self._cmds = []
        self._interactions = {}

    def _determine_cost(self, mapping):
        """
        Determine the cost of the circuit with the given mapping.

        Args:
            mapping (dict): Dictionary with key, value pairs where keys are logical qubit ids and the corresponding
                value is the physical location on the IBM Q chip.
        Returns:
            Cost measure taking into account CNOT directionality or None if the circuit cannot be executed given the
            mapping.
        """
        cost = 0
        for tpl, interaction in self._interactions.items():
            ctrl_id = tpl[0]
            target_id = tpl[1]
            ctrl_pos = mapping[ctrl_id]
            target_pos = mapping[target_id]
            if not (ctrl_pos, target_pos) in self.connections:
                if (target_pos, ctrl_pos) in self.connections:
                    cost += interaction
                else:
                    return None
        return cost

    def _run(self):
        """
        Run all stored gates.

        Raises:
            Exception:
                If the mapping to the IBM backend cannot be performed or if the mapping was already determined but
                more CNOTs get sent down the pipeline.
        """
        if len(self.current_mapping) > 0 and max(self.current_mapping.values()) > 4:
            raise RuntimeError(
                "Too many qubits allocated. The IBM Q "
                "device supports at most 5 qubits and no "
                "intermediate measurements / "
                "reallocations."
            )
        if len(self._interactions) > 0:
            logical_ids = list(self.current_mapping)
            best_mapping = self.current_mapping
            best_cost = None
            for physical_ids in itertools.permutations(list(range(5)), len(logical_ids)):
                mapping = {logical_ids[i]: physical_ids[i] for i in range(len(logical_ids))}
                new_cost = self._determine_cost(mapping)
                if new_cost is not None:
                    if best_cost is None or new_cost < best_cost:
                        best_cost = new_cost
                        best_mapping = mapping
            if best_cost is None:
                raise RuntimeError("Circuit cannot be mapped without using Swaps. Mapping failed.")
            self._interactions = {}
            self.current_mapping = best_mapping

        for cmd in self._cmds:
            self._send_cmd_with_mapped_ids(cmd)

        self._cmds = []

    def _store(self, cmd):
        """
        Store a command and handle CNOTs.

        Args:
            cmd (Command): A command to store
        """
        if not cmd.gate == FlushGate():
            target = cmd.qubits[0][0].id
        if _is_cnot(cmd):
            # CNOT encountered
            ctrl = cmd.control_qubits[0].id
            if not (ctrl, target) in self._interactions:
                self._interactions[(ctrl, target)] = 0
            self._interactions[(ctrl, target)] += 1
        elif cmd.gate == Allocate:
            if target not in self.current_mapping:
                new_max = 0
                if len(self.current_mapping) > 0:
                    new_max = max(self.current_mapping.values()) + 1
                self._current_mapping[target] = new_max
        self._cmds.append(cmd)

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a command list and, for each command, stores it until completion.

        Args:
            command_list (list of Command objects): list of commands to
                receive.

        Raises:
            Exception: If mapping the CNOT gates to 1 qubit would require Swaps. The current version only supports
                remapping of CNOT gates without performing any Swaps due to the large costs associated with Swapping
                given the CNOT constraints.
        """
        for cmd in command_list:
            self._store(cmd)
            if isinstance(cmd.gate, FlushGate):
                self._run()
                self._reset()

def _is_cnot(cmd):
    """
    Check if the command corresponds to a CNOT (controlled NOT gate).

    Args:
        cmd (Command): Command to check whether it is a controlled NOT
            gate.
    """
    return isinstance(cmd.gate, NOT.__class__) and get_control_count(cmd) == 1