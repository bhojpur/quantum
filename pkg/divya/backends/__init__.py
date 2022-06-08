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
Contains back-ends for Divya.

This includes:

* a debugging tool to print all received commands (CommandPrinter)
* a circuit drawing engine (which can be used anywhere within the compilation
  chain)
* a simulator with emulation capabilities
* a resource counter (counts gates and keeps track of the maximal width of the
  circuit)
* an interface to the IBM Quantum Experience chip (and simulator).
* an interface to the AQT trapped ion system (and simulator).
* an interface to the AWS Braket service decives (and simulators)
* an interface to the IonQ trapped ionq hardware (and simulator).
"""
from ._aqt import AQTBackend
from ._awsbraket import AWSBraketBackend
from ._circuits import CircuitDrawer, CircuitDrawerMatplotlib
from ._exceptions import DeviceNotHandledError, DeviceOfflineError, DeviceTooSmall
from ._ibm import IBMBackend
from ._ionq import IonQBackend
from ._printer import CommandPrinter
from ._resource import ResourceCounter
from ._sim import ClassicalSimulator, Simulator
from ._unitary import UnitarySimulator