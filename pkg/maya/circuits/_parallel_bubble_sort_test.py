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

"""Tests for _parallel_bubble_sort.py."""
import unittest

from maya.circuits._parallel_bubble_sort import (
    index_of_position_in_1d_array, is_sorted_array_of_nd_positions,
    parallel_bubble_sort)


class IndexTest(unittest.TestCase):
    def test_index_standard_order_coordinates(self):
        self.assertEqual(
            index_of_position_in_1d_array(
                (2, 1, 0), 3, (1, 2, 3)),
            ((3 ** 2) * 1 + (3 ** 1) * 2 + (3 ** 0) * 3))

    def test_index_reverse_order_coordinates(self):
        self.assertEqual(
            index_of_position_in_1d_array(
                (0, 1, 2), 3, (2, 3, 5)),
            ((3 ** 0) * 2 + (3 ** 1) * 3 + (3 ** 2) * 5))

    def test_index_scrambled_coordinates(self):
        self.assertEqual(
            index_of_position_in_1d_array(
                (2, 0, 1), 4, (2, 1, 0)),
            ((4 ** 2) * 2 + (4 ** 0) * 1 + (4 ** 1) * 0))

    def test_index_scrambled_coordinates_6dimensions(self):
        self.assertEqual(
            index_of_position_in_1d_array(
                (1, 2, 0, 5, 4, 3), 3, (2, 1, 0, 0, 1, 2)),
            (3 ** 1) * 2 + (3 ** 2) + (3 ** 4) + (3 ** 3) * 2)


class IsSortedTest(unittest.TestCase):
    def test_is_sorted_standard_order(self):
        key = (index_of_position_in_1d_array, (2, 1, 0))
        arr = [(0, 0, i) for i in range(7)]
        self.assertTrue(is_sorted_array_of_nd_positions(arr, key, 7))

    def test_not_is_sorted_reverse_ordered_list(self):
        key = (index_of_position_in_1d_array, (2, 1, 0))
        arr = [(0, 0, i) for i in range(7, -1, -1)]
        self.assertFalse(is_sorted_array_of_nd_positions(arr, key, 7))

    def test_is_sorted_3d(self):
        key = (index_of_position_in_1d_array, (2, 1, 0))
        arr = [(i, j, k) for i in range(8)
               for j in range(8)
               for k in range(8)]
        self.assertTrue(is_sorted_array_of_nd_positions(arr, key, 8))

    def test_not_is_sorted_2d_last_elements_swapped(self):
        key = (index_of_position_in_1d_array, (1, 0))
        arr = [(i, j) for i in range(12) for j in range(12)]
        arr[-1], arr[-2] = arr[-2], arr[-1]
        self.assertFalse(is_sorted_array_of_nd_positions(arr, key, 12))


class ParallelBubbleSort1DTest(unittest.TestCase):
    def test_sort_4_elements(self):
        key = (index_of_position_in_1d_array, (2, 1, 0))
        arr = [(1, 0, 0), (0, 0, 1), (0, 1, 0), (0, 0, 0)]
        parallel_bubble_sort(arr, key, system_side_length=2)
        self.assertListEqual(arr,
                             [(0, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0)])

    def test_sort_reverse_long_no_optional_parameters_specified(self):
        key = (index_of_position_in_1d_array, (2, 0, 1))
        arr = [(0, i, 0) for i in range(10, -1, -1)]
        parallel_bubble_sort(arr, key, system_side_length=11)
        self.assertListEqual(arr, [(0, i, 0) for i in range(11)])

    def test_sort_scrambled(self):
        key = (index_of_position_in_1d_array, (0, 1))
        arr = [(1, 2), (0, 1), (2, 1), (1, 0), (0, 0), (2, 0)]
        parallel_bubble_sort(arr, key, system_side_length=3)
        self.assertListEqual(arr, [(0, 0), (1, 0), (2, 0),
                                   (0, 1), (2, 1), (1, 2)])

    def test_sort_already_sorted(self):
        key = (index_of_position_in_1d_array, (2, 1, 0))
        arr = [(0, i, j) for i in range(5) for j in range(5)]
        parallel_bubble_sort(arr, key, system_side_length=5)
        self.assertListEqual(arr, [(0, i, j) for i in range(5)
                                   for j in range(5)])


class ParallelBubbleSortIntegrationTest(unittest.TestCase):
    def test_sort_2d_grid_embedded_in_1d_array_integration_test(self):
        from functools import partial

        key_2d = partial(index_of_position_in_1d_array, (0, 1))
        system_size = 8
        arr = [(i, j) for i in range(system_size)
               for j in range(system_size)]

        self.assertListEqual(list(map(partial(key_2d, system_size), arr))[:16],
                             list(range(0, 64, 8)) + list(range(1, 65, 8)))

        self.assertFalse(is_sorted_array_of_nd_positions(arr, key_2d,
                                                         system_size))
        swaps = parallel_bubble_sort(arr, key_2d, system_size)
        self.assertEqual(len(swaps), 50)
        self.assertTrue(is_sorted_array_of_nd_positions(arr, key_2d,
                                                        system_size))

    def test_ffft_like_sorting(self):
        # Determine how to order the modes for correct input to the FFFT.
        system_size = 8
        s = '{:0' + str(3) + 'b}'
        first_round = [int(s.format(i)[::-1], 2) for i in range(system_size)]
        second_round = (list(range(system_size // 2, system_size)) +
                        list(range(system_size // 2)))

        # Generate array of size system_size.
        arr = [(i,) for i in range(system_size)]

        # Create arrays whose swap networks to resort are the same as should
        # be applied to the fermionic modes.
        arr_first = [None] * system_size
        arr_second = [None] * system_size
        for i in range(system_size):
            arr_first[i] = (first_round[arr[i][0]],)
            arr_second[i] = (second_round[arr[i][0]],)

        # Find the two rounds of swaps for parallel bubble sort into
        # row-major order.
        key = (index_of_position_in_1d_array, (0,))
        first_round_swaps = parallel_bubble_sort(arr_first, key, system_size)
        second_round_swaps = parallel_bubble_sort(arr_second, key, system_size)

        # Create the full list of swaps.
        swap_mode_list = first_round_swaps + second_round_swaps[::-1]
        swaps = [swap[0] for swap_layer in swap_mode_list
                 for swap in swap_layer]

        # Compare with the correct full swap network for the FFFT.
        self.assertListEqual(swaps, [1, 3, 5, 2, 4, 1, 3, 5, 3, 2, 4,
                                     1, 3, 5, 0, 2, 4, 6, 1, 3, 5, 2, 4, 3])