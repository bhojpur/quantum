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

"""Tools to add/remove compiler engines to the MainEngine list."""

def insert_engine(prev_engine, engine_to_insert):
    """
    Insert an engine into the singly-linked list of engines.

    It also sets the correct main_engine for engine_to_insert.

    Args:
        prev_engine (divya.cengines.BasicEngine): The engine just before the insertion point.
        engine_to_insert (divya.cengines.BasicEngine): The engine to insert at the insertion point.
    """
    if prev_engine.main_engine is not None:
        prev_engine.main_engine.n_engines += 1

        if prev_engine.main_engine.n_engines > prev_engine.main_engine.n_engines_max:
            raise RuntimeError('Too many compiler engines added to the MainEngine!')

    engine_to_insert.main_engine = prev_engine.main_engine
    engine_to_insert.next_engine = prev_engine.next_engine
    prev_engine.next_engine = engine_to_insert


def drop_engine_after(prev_engine):
    """
    Remove an engine from the singly-linked list of engines.

    Args:
        prev_engine (divya.cengines.BasicEngine): The engine just before the engine to drop.

    Returns:
        Engine: The dropped engine.
    """
    dropped_engine = prev_engine.next_engine
    prev_engine.next_engine = dropped_engine.next_engine
    if prev_engine.main_engine is not None:
        prev_engine.main_engine.n_engines -= 1
    dropped_engine.next_engine = None
    dropped_engine.main_engine = None
    return dropped_engine