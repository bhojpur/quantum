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

import itertools

class Grid:
    """
    A multi-dimensional grid of points.
    """

    def __init__(self, dimensions, length, scale):
        """
        Args:
            dimensions (int): The number of dimensions the grid lives in.
            length (int): The number of points along each grid axis.
            scale (float): The total length of each grid dimension.
        """
        if not isinstance(dimensions, int) or dimensions < 0:
            raise ValueError(
                'dimensions must be a non-negative int but was {} {}'.format(
                    type(dimensions), repr(dimensions)))
        if not isinstance(length, int) or length < 0:
            raise ValueError(
                'length must be a non-negative int but was {} {}'.format(
                    type(length), repr(length)))
        if not isinstance(scale, float) or not scale > 0:
            raise ValueError(
                'scale must be a positive float but was {} {}'.format(
                    type(scale), repr(scale)))

        self.dimensions = dimensions
        self.length = length
        self.scale = scale

    def volume_scale(self):
        """
        Returns:
            float: The volume of a length-scale hypercube within the grid.
        """
        return self.scale ** float(self.dimensions)

    def num_points(self):
        """
        Returns:
            int: The number of points in the grid.
        """
        return self.length ** self.dimensions

    def all_points_indices(self):
        """
        Returns:
            iterable[tuple[int]]:
                The index-coordinate tuple of each point in the grid.
        """
        return itertools.product(range(self.length), repeat=self.dimensions)