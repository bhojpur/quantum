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

"""Tests for divya.cengines._tagremover.py."""

import pytest

from divya import MainEngine
from divya.cengines import DummyEngine, _tagremover
from divya.meta import ComputeTag, UncomputeTag
from divya.ops import Command, H

def test_tagremover_default():
    tag_remover = _tagremover.TagRemover()
    assert tag_remover._tags == [ComputeTag, UncomputeTag]

def test_tagremover_invalid():
    with pytest.raises(TypeError):
        _tagremover.TagRemover(ComputeTag)

def test_tagremover():
    backend = DummyEngine(save_commands=True)
    tag_remover = _tagremover.TagRemover([type("")])
    eng = MainEngine(backend=backend, engine_list=[tag_remover])
    # Create a command_list and check if "NewTag" is removed
    qubit = eng.allocate_qubit()
    cmd0 = Command(eng, H, (qubit,))
    cmd0.tags = ["NewTag"]
    cmd1 = Command(eng, H, (qubit,))
    cmd1.tags = [1, 2, "NewTag", 3]
    cmd_list = [cmd0, cmd1, cmd0]
    assert len(backend.received_commands) == 1  # AllocateQubitGate
    tag_remover.receive(cmd_list)
    assert len(backend.received_commands) == 4
    assert backend.received_commands[1].tags == []
    assert backend.received_commands[2].tags == [1, 2, 3]