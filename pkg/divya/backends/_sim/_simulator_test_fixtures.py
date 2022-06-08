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

import pytest

from divya.cengines import BasicMapperEngine

@pytest.fixture(params=["mapper", "no_mapper"])
def mapper(request):
    """Add a mapper which changes qubit ids by adding 1."""
    if request.param == "mapper":

        class TrivialMapper(BasicMapperEngine):
            def __init__(self):
                super().__init__()
                self.current_mapping = {}

            def receive(self, command_list):
                for cmd in command_list:
                    for qureg in cmd.all_qubits:
                        for qubit in qureg:
                            if qubit.id == -1:
                                continue
                            elif qubit.id not in self.current_mapping:
                                previous_map = self.current_mapping
                                previous_map[qubit.id] = qubit.id + 1
                                self.current_mapping = previous_map
                    self._send_cmd_with_mapped_ids(cmd)

        return TrivialMapper()
    if request.param == "no_mapper":
        return None