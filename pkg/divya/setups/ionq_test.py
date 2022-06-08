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

"""Tests for divya.setup.ionq."""

import pytest

from divya.backends._exceptions import DeviceOfflineError
from divya.backends._ionq._ionq_http_client import IonQ
from divya.backends._ionq._ionq_mapper import BoundedQubitMapper

def test_basic_ionq_mapper(monkeypatch):
    import divya.setups.ionq

    def mock_show_devices(*args, **kwargs):
        return {'dummy': {'nq': 3, 'target': 'dummy'}}

    monkeypatch.setattr(
        IonQ,
        'show_devices',
        mock_show_devices,
    )
    engine_list = divya.setups.ionq.get_engine_list(device='dummy')
    assert len(engine_list) > 1
    mapper = engine_list[-1]
    assert isinstance(mapper, BoundedQubitMapper)
    # to match nq in the backend
    assert mapper.max_qubits == 3

def test_ionq_errors(monkeypatch):
    import divya.setups.ionq

    def mock_show_devices(*args, **kwargs):
        return {'dummy': {'nq': 3, 'target': 'dummy'}}

    monkeypatch.setattr(
        IonQ,
        'show_devices',
        mock_show_devices,
    )

    with pytest.raises(DeviceOfflineError):
        divya.setups.ionq.get_engine_list(device='simulator')