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

"""A compiler engine to add mapping information."""

from ._basicmapper import BasicMapperEngine

class ManualMapper(BasicMapperEngine):
    """
    Manual Mapper which adds QubitPlacementTags to Allocate gate commands according to a user-specified mapping.

    Attributes:
        map (function): The function which maps a given qubit id to its location. It gets set when initializing the
            mapper.
    """

    def __init__(self, map_fun=lambda x: x):
        """
        Initialize the mapper to a given mapping.

        If no mapping function is provided, the qubit id is used as the location.

        Args:
            map_fun (function): Function which, given the qubit id, returns an integer describing the physical
                location (must be constant).
        """
        super().__init__()
        self.map = map_fun
        self.current_mapping = {}

    def receive(self, command_list):
        """
        Receives a command list and passes it to the next engine, adding qubit placement tags to allocate gates.

        Args:
            command_list (list of Command objects): list of commands to receive.
        """
        for cmd in command_list:
            ids = [qb.id for qr in cmd.qubits for qb in qr]
            ids += [qb.id for qb in cmd.control_qubits]
            for qubit_id in ids:
                if qubit_id not in self.current_mapping:
                    self._current_mapping[qubit_id] = self.map(qubit_id)
            self._send_cmd_with_mapped_ids(cmd)