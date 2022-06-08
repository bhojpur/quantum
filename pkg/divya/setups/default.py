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
The default setup which provides an `engine_list` for the `MainEngine`.

It contains `LocalOptimizers` and an `AutoReplacer` which uses most of the decompositions rules defined in
divya.setups.decompositions
"""

import divya
import divya.setups.decompositions
from divya.cengines import (
    AutoReplacer,
    DecompositionRuleSet,
    LocalOptimizer,
    TagRemover,
)

def get_engine_list():
    """Return the default list of compiler engine."""
    rule_set = DecompositionRuleSet(modules=[divya.setups.decompositions])
    return [TagRemover(), LocalOptimizer(10), AutoReplacer(rule_set), TagRemover(), LocalOptimizer(10)]