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
The divya.meta package features meta instructions which help both the user and the compiler in writing/producing
efficient code. It includes, e.g.,

* Loop (with Loop(eng): ...)
* Compute/Uncompute (with Compute(eng): ..., [...], Uncompute(eng))
* Control (with Control(eng, ctrl_qubits): ...)
* Dagger (with Dagger(eng): ...)
"""

from ._compute import Compute, ComputeTag, CustomUncompute, Uncompute, UncomputeTag
from ._control import (
    Control,
    canonical_ctrl_state,
    get_control_count,
    has_negative_control,
)
from ._dagger import Dagger
from ._dirtyqubit import DirtyQubitTag
from ._logicalqubit import LogicalQubitIDTag
from ._loop import Loop, LoopTag
from ._util import drop_engine_after, insert_engine