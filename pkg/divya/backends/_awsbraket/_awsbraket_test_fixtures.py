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

# This file contains:
#
# - Helper fixtures:
#   * arntask
#   * creds
#   * s3_folder
#   * device_value
#   * search_value
#   * completed_value
# - Setup fixtures for specific tests:
#   * sent_error_setup
#   * retrieve_setup
#   * functional_setup

"""Define test fixtures for the AWSBraket backend."""

import json
from io import StringIO

import pytest

try:
    from botocore.response import StreamingBody
except ImportError:

    class StreamingBody:
        """Dummy implementation of a StreamingBody."""

        def __init__(self, raw_stream, content_length):
            """Initialize a dummy StreamingBody."""

# ==============================================================================

@pytest.fixture
def arntask():
    """Define an ARNTask test setup."""
    return 'arn:aws:braket:us-east-1:id:retrieve_execution'

@pytest.fixture
def creds():
    """Credentials test setup."""
    return {
        'AWS_ACCESS_KEY_ID': 'aws_access_key_id',
        'AWS_SECRET_KEY': 'aws_secret_key',
    }

@pytest.fixture
def s3_folder():
    """S3 folder value test setup."""
    return ['S3Bucket', 'S3Directory']

@pytest.fixture
def device_value():
    """Device value test setup."""
    device_value_devicecapabilities = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.device_schema.rigetti.rigetti_device_capabilities",
                "version": "1",
            },
            "service": {
                "executionWindows": [
                    {
                        "executionDay": "Everyday",
                        "windowStartHour": "11:00",
                        "windowEndHour": "12:00",
                    }
                ],
                "shotsRange": [1, 10],
                "deviceLocation": "us-east-1",
            },
            "action": {
                "braket.ir.jaqcd.program": {
                    "actionType": "braket.ir.jaqcd.program",
                    "version": ["1"],
                    "supportedOperations": ["H"],
                }
            },
            "paradigm": {
                "qubitCount": 30,
                "nativeGateSet": ["ccnot", "cy"],
                "connectivity": {
                    "fullyConnected": False,
                    "connectivityGraph": {"1": ["2", "3"]},
                },
            },
            "deviceParameters": {
                "properties": {
                    "braketSchemaHeader": {
                        "const": {
                            "name": "braket.device_schema.rigetti.rigetti_device_parameters",
                            "version": "1",
                        }
                    }
                },
                "definitions": {
                    "GateModelParameters": {
                        "properties": {
                            "braketSchemaHeader": {
                                "const": {
                                    "name": "braket.device_schema.gate_model_parameters",
                                    "version": "1",
                                }
                            }
                        }
                    }
                },
            },
        }
    )

    return {
        "deviceName": "Aspen-8",
        "deviceType": "QPU",
        "providerName": "provider1",
        "deviceStatus": "OFFLINE",
        "deviceCapabilities": device_value_devicecapabilities,
    }

@pytest.fixture
def search_value():
    """Search value test setup."""
    return {
        "devices": [
            {
                "deviceArn": "arn1",
                "deviceName": "name1",
                "deviceType": "SIMULATOR",
                "deviceStatus": "ONLINE",
                "providerName": "pname1",
            },
            {
                "deviceArn": "arn2",
                "deviceName": "name2",
                "deviceType": "QPU",
                "deviceStatus": "OFFLINE",
                "providerName": "pname1",
            },
            {
                "deviceArn": "arn3",
                "deviceName": "Aspen-8",
                "deviceType": "QPU",
                "deviceStatus": "ONLINE",
                "providerName": "pname2",
            },
        ]
    }

@pytest.fixture
def completed_value():
    """Completed value test setup."""
    return {
        'deviceArn': 'arndevice',
        'deviceParameters': 'parameters',
        'outputS3Bucket': 'amazon-braket-bucket',
        'outputS3Directory': 'complete/directory',
        'quantumTaskArn': 'arntask',
        'shots': 123,
        'status': 'COMPLETED',
        'tags': {'tagkey': 'tagvalue'},
    }

# ==============================================================================

@pytest.fixture
def sent_error_setup(creds, s3_folder, device_value, search_value):
    """Send error test setup."""
    return creds, s3_folder, search_value, device_value

@pytest.fixture
def results_json():
    """Results test setup."""
    return json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.gate_model_task_result",
                "version": "1",
            },
            "measurementProbabilities": {
                "0000": 0.04,
                "0010": 0.06,
                "0110": 0.2,
                "0001": 0.3,
                "1001": 0.5,
            },
            "measuredQubits": [0, 1, 2],
        }
    )

@pytest.fixture
def retrieve_setup(arntask, creds, device_value, completed_value, results_json):
    """Retrieve test setup."""
    body = StreamingBody(StringIO(results_json), len(results_json))

    results_dict = {
        'ResponseMetadata': {
            'RequestId': 'CF4CAA48CC18836C',
            'HTTPHeaders': {},
        },
        'Body': body,
    }

    return arntask, creds, completed_value, device_value, results_dict

@pytest.fixture
def functional_setup(arntask, creds, s3_folder, search_value, device_value, completed_value, results_json):
    """Functional test setup."""
    qtarntask = {'quantumTaskArn': arntask}
    body2 = StreamingBody(StringIO(results_json), len(results_json))
    results_dict = {
        'ResponseMetadata': {
            'RequestId': 'CF4CAA48CC18836C',
            'HTTPHeaders': {},
        },
        'Body': body2,
    }

    return (
        creds,
        s3_folder,
        search_value,
        device_value,
        qtarntask,
        completed_value,
        results_dict,
    )

# ==============================================================================