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

from __future__ import absolute_import

import unittest

from maya.utils import Grid

class GridTest(unittest.TestCase):

    def test_preconditions(self):
        nan = float('nan')

        # No exception
        _ = Grid(dimensions=0, length=0, scale=1.0)
        _ = Grid(dimensions=1, length=1, scale=1.0)
        _ = Grid(dimensions=2, length=3, scale=0.01)
        _ = Grid(dimensions=234, length=345, scale=456.0)

        with self.assertRaises(ValueError):
            _ = Grid(dimensions=1, length=1, scale=1)
        with self.assertRaises(ValueError):
            _ = Grid(dimensions=1, length=1, scale=0.0)
        with self.assertRaises(ValueError):
            _ = Grid(dimensions=1, length=1, scale=-1.0)
        with self.assertRaises(ValueError):
            _ = Grid(dimensions=1, length=1, scale=nan)

        with self.assertRaises(ValueError):
            _ = Grid(dimensions=1, length=-1, scale=1.0)
        with self.assertRaises(ValueError):
            _ = Grid(dimensions=-1, length=1, scale=1.0)

    def test_properties(self):
        g = Grid(dimensions=2, length=3, scale=5.0)
        self.assertEqual(g.num_points(), 9)
        self.assertEqual(g.volume_scale(), 25)
        self.assertEqual(list(g.all_points_indices()), [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 0),
            (1, 1),
            (1, 2),
            (2, 0),
            (2, 1),
            (2, 2),
        ])