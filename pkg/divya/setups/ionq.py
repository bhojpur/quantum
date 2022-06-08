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
A setup for IonQ trapped ion devices.

Defines a setup allowing to compile code for IonQ trapped ion devices:
->The 11 qubit device
->The 29 qubits simulator
"""
from divya.backends._exceptions import DeviceOfflineError
from divya.backends._ionq._ionq_http_client import IonQ
from divya.backends._ionq._ionq_mapper import BoundedQubitMapper
from divya.ops import (
    Barrier,
    H,
    Rx,
    Rxx,
    Ry,
    Ryy,
    Rz,
    Rzz,
    S,
    Sdag,
    SqrtX,
    Swap,
    T,
    Tdag,
    X,
    Y,
    Z,
)
from divya.setups import restrictedgateset

def get_engine_list(token=None, device=None):
    """Return the default list of compiler engine for the IonQ platform."""
    service = IonQ()
    if token is not None:
        service.authenticate(token=token)
    devices = service.show_devices()
    if not device or device not in devices:
        raise DeviceOfflineError("Error checking engine list: no '{}' devices available".format(device))

    #
    # Qubit mapper
    #
    mapper = BoundedQubitMapper(devices[device]['nq'])

    #
    # Basis Gates
    #

    # Declare the basis gateset for the IonQ's API.
    engine_list = restrictedgateset.get_engine_list(
        one_qubit_gates=(X, Y, Z, Rx, Ry, Rz, H, S, Sdag, T, Tdag, SqrtX),
        two_qubit_gates=(Swap, Rxx, Ryy, Rzz),
        other_gates=(Barrier,),
    )
    return engine_list + [mapper]

__all__ = ['get_engine_list']