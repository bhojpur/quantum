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
A CommandModifier engine that can be used to apply a user-defined transformation to all incoming commands.

A CommandModifier engine can be used to, e.g., modify the tags of all commands which pass by (see the
AutoReplacer for an example).
"""

from ._basics import BasicEngine

class CommandModifier(BasicEngine):
    """
    Compiler engine applying a user-defined transformation to all incoming commands.

    CommandModifier is a compiler engine which applies a function to all incoming commands, sending on the resulting
    command instead of the original one.
    """

    def __init__(self, cmd_mod_fun):
        """
        Initialize the CommandModifier.

        Args:
            cmd_mod_fun (function): Function which, given a command cmd, returns the command it should send instead.

        Example:
            .. code-block:: python

                def cmd_mod_fun(cmd):
                    cmd.tags += [MyOwnTag()]
                compiler_engine = CommandModifier(cmd_mod_fun)
                ...
        """
        super().__init__()
        self._cmd_mod_fun = cmd_mod_fun

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a list of commands from the previous engine, modify all commands, and send them on to the next engine.

        Args:
            command_list (list<Command>): List of commands to receive and then (after modification) send on.
        """
        new_command_list = [self._cmd_mod_fun(cmd) for cmd in command_list]
        self.send(new_command_list)