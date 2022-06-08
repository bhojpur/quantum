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

"""Tests for divya.setup.aqt."""

import pytest

def test_aqt_mapper_in_cengines(monkeypatch):
    import divya.setups.aqt

    def mock_show_devices(*args, **kwargs):
        connections = {
            (0, 1),
            (1, 0),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 1),
            (2, 3),
            (2, 4),
            (3, 1),
            (3, 4),
            (4, 3),
        }
        return {'aqt_simulator': {'coupling_map': connections, 'version': '0.0.0', 'nq': 32}}

    monkeypatch.setattr(divya.setups.aqt, "show_devices", mock_show_devices)
    engines_simulator = divya.setups.aqt.get_engine_list(device='aqt_simulator')
    assert len(engines_simulator) == 13

def test_aqt_errors(monkeypatch):
    import divya.setups.aqt

    def mock_show_devices(*args, **kwargs):
        connections = {
            (0, 1),
            (1, 0),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 1),
            (2, 3),
            (2, 4),
            (3, 1),
            (3, 4),
            (4, 3),
        }
        return {'aqt_imaginary': {'coupling_map': connections, 'version': '0.0.0', 'nq': 6}}

    monkeypatch.setattr(divya.setups.aqt, "show_devices", mock_show_devices)
    with pytest.raises(divya.setups.aqt.DeviceOfflineError):
        divya.setups.aqt.get_engine_list(device='simulator')
    with pytest.raises(divya.setups.aqt.DeviceNotHandledError):
        divya.setups.aqt.get_engine_list(device='aqt_imaginary')