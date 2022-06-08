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
A setup for AQT trapped ion devices.

Defines a setup allowing to compile code for the AQT trapped ion devices:
->The 4 qubits device
->The 11 qubits simulator
->The 11 qubits noisy simulator

It provides the `engine_list` for the `MainEngine' based on the requested
device.  Decompose the circuit into a Rx/Ry/Rxx gate set that will be
translated in the backend in the Rx/Ry/MS gate set.
"""

from divya.backends._aqt._aqt_http_client import show_devices
from divya.backends._exceptions import DeviceNotHandledError, DeviceOfflineError
from divya.cengines import BasicMapperEngine
from divya.ops import Barrier, Rx, Rxx, Ry
from divya.setups import restrictedgateset


def get_engine_list(token=None, device=None):
    """Return the default list of compiler engine for the AQT plaftorm."""
    # Access to the hardware properties via show_devices
    # Can also be extended to take into account gate fidelities, new available
    # gate, etc..
    devices = show_devices(token)
    aqt_setup = []
    if device not in devices:
        raise DeviceOfflineError('Error when configuring engine list: device requested for Backend not connected')
    if device == 'aqt_simulator':
        # The 11 qubit online simulator doesn't need a specific mapping for
        # gates. Can also run wider gateset but this setup keep the
        # restrictedgateset setup for coherence
        mapper = BasicMapperEngine()
        # Note: Manual Mapper doesn't work, because its map is updated only if
        # gates are applied if gates in the register are not used, then it
        # will lead to state errors
        res = {}
        for i in range(devices[device]['nq']):
            res[i] = i
        mapper.current_mapping = res
        aqt_setup = [mapper]
    else:
        # If there is an online device not handled into Bhojpur Quantum it's not too
        # bad, the engine_list can be constructed manually with the
        # appropriate mapper and the 'coupling_map' parameter
        raise DeviceNotHandledError('Device not yet fully handled by Bhojpur Quantum')

    # Most gates need to be decomposed into a subset that is manually converted
    # in the backend (until the implementation of the U1,U2,U3)
    setup = restrictedgateset.get_engine_list(one_qubit_gates=(Rx, Ry), two_qubit_gates=(Rxx,), other_gates=(Barrier,))
    setup.extend(aqt_setup)
    return setup