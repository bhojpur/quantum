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

"""Tests for divya.cengines._cmdmodifier.py."""

from divya import MainEngine
from divya.cengines import DummyEngine, _cmdmodifier
from divya.ops import ClassicalInstructionGate, FastForwardingGate, H

def test_command_modifier():
    def cmd_mod_fun(cmd):
        cmd.tags = "NewTag"
        return cmd

    backend = DummyEngine(save_commands=True)
    cmd_modifier = _cmdmodifier.CommandModifier(cmd_mod_fun)
    main_engine = MainEngine(backend=backend, engine_list=[cmd_modifier])
    qubit = main_engine.allocate_qubit()
    H | qubit
    # Test if H gate was sent through forwarder_eng and tag was added
    received_commands = []
    # Remove Allocate and Deallocate gates
    for cmd in backend.received_commands:
        if not (isinstance(cmd.gate, FastForwardingGate) or isinstance(cmd.gate, ClassicalInstructionGate)):
            received_commands.append(cmd)
    for cmd in received_commands:
        print(cmd)
    assert len(received_commands) == 1
    assert received_commands[0].gate == H
    assert received_commands[0].tags == "NewTag"