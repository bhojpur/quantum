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
The TagRemover compiler engine.

A TagRemover engine removes temporary command tags (such as Compute/Uncompute), thus enabling optimization across meta
statements (loops after unrolling, compute/uncompute, ...)
"""
from divya.meta import ComputeTag, UncomputeTag

from ._basics import BasicEngine

class TagRemover(BasicEngine):
    """
    Compiler engine that remove temporary command tags.

    TagRemover is a compiler engine which removes temporary command tags (see the tag classes such as LoopTag in
    divya.meta._loop).

    Removing tags is important (after having handled them if necessary) in order to enable optimizations across
    meta-function boundaries (compute/ action/uncompute or loops after unrolling)
    """

    def __init__(self, tags=None):
        """
        Initialize a TagRemover object.

        Args:
            tags: A list of meta tag classes (e.g., [ComputeTag, UncomputeTag])
                denoting the tags to remove
        """
        super().__init__()
        if not tags:
            self._tags = [ComputeTag, UncomputeTag]
        elif isinstance(tags, list):
            self._tags = tags
        else:
            raise TypeError('tags should be a list! Got: {}'.format(tags))

    def receive(self, command_list):
        """
        Receive a list of commands.

        Receive a list of commands from the previous engine, remove all tags which are an instance of at least one of
        the meta tags provided in the constructor, and then send them on to the next compiler engine.

        Args:
            command_list (list<Command>): List of commands to receive and then (after removing tags) send on.
        """
        for cmd in command_list:
            for tag in self._tags:
                cmd.tags = [t for t in cmd.tags if not isinstance(t, tag)]
            self.send([cmd])