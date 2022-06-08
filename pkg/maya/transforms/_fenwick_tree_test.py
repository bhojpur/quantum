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

"""Tests for Fenwick tree module."""
from __future__ import absolute_import

import unittest

from maya.transforms._fenwick_tree import FenwickNode, FenwickTree

class FenwickTreeTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_fenwick_tree_structure(self):
        """A lookup test on 5-qubit fenwick tree.

        Test:    Verifies structure of the Fenwick Tree on 5 sites.

        """

        f = FenwickTree(5)
        self.assertEqual(f.root.children[0].index, 2)
        self.assertEqual(f.root.children[1].index, 3)
        self.assertEqual(f.root.children[0].children[0].index, 1)
        self.assertEqual(f.root.children[0].children[0].children[0].index, 0)

    def test_fenwick_tree_ancestors(self):
        """Ancestor test. Check validity of the get_update_set(j) method on 8
        qubit register. Note that root is the last node.

        Test:     Verifies integrity of ancestors of nodes within the
        tree.

        """

        f = FenwickTree(8)
        self.assertEqual(len(f.get_update_set(7)), 0)

        # Is the parent of the middle child the root?
        self.assertEqual(f.get_update_set(3)[0], f.root)

        # Are the ancestors chained correctly?
        self.assertEqual(f.get_update_set(0)[0], f.get_node(1))
        self.assertEqual(f.get_update_set(0)[1], f.get_node(3))

    def test_fenwick_tree_children(self):
        """Children test. Checks get_F(j) on 8 qubit register.

        Test:     Verifies integrity of child nodes of the root.

        """

        f = FenwickTree(8)
        self.assertEqual(f.get_node(7).children[0], f.get_node(3))
        self.assertEqual(f.get_node(7).children[1], f.get_node(5))
        self.assertEqual(f.get_node(7).children[2], f.get_node(6))

    def test_fenwick_tree_ancestor_children(self):
        """Ancestor children test. Checks get_remainder_set(j) on 8 qubit
        register.

        Tests:    Checks the example given in the paper.

        """

        # TODO: Possibly too weak.
        f = FenwickTree(16)
        self.assertEqual(f.get_remainder_set(9)[0].index, 7)


if __name__ == '__main__':
    unittest.main()