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

"""Bhojpur Quantum module containing all compiler engines."""

from ._basics import BasicEngine, ForwarderEngine, LastEngineException  # isort:skip
from ._cmdmodifier import CommandModifier  # isort:skip
from ._basicmapper import BasicMapperEngine  # isort:skip

from ._ibm5qubitmapper import IBM5QubitMapper
from ._linearmapper import LinearMapper, return_swap_depth
from ._main import MainEngine, NotYetMeasuredError, UnsupportedEngineError
from ._manualmapper import ManualMapper
from ._optimize import LocalOptimizer
from ._replacer import (
    AutoReplacer,
    DecompositionRule,
    DecompositionRuleSet,
    InstructionFilter,
)
from ._swapandcnotflipper import SwapAndCNOTFlipper
from ._tagremover import TagRemover
from ._testengine import CompareEngine, DummyEngine
from ._twodmapper import GridMapper