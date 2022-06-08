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

"""Exception classes for divya.backends."""

class DeviceTooSmall(Exception):
    """Raised when a device does not have enough qubits for a desired job."""

class DeviceOfflineError(Exception):
    """Raised when a device is required but is currently offline."""

class DeviceNotHandledError(Exception):
    """Exception raised if a selected device cannot handle the circuit or is not supported by divya."""

class RequestTimeoutError(Exception):
    """Raised if a request to the job creation API times out."""

class JobSubmissionError(Exception):
    """Raised when the job creation API contains an error of some kind."""

class InvalidCommandError(Exception):
    """Raised if the backend encounters an invalid command."""

class MidCircuitMeasurementError(Exception):
    """Raised when a mid-circuit measurement is detected on a qubit."""