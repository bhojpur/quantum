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
#   * info
#   * results_json
#   * results_dict
#   * res_completed
#   * search_value
#   * device_value
#   * devicelist_result
# - Setup fixtures for specific tests:
#   * show_devices_setup
#   * retrieve_setup
#   * retrieve_devicetypes_setup
#   * send_too_many_setup
#   * real_device_online_setup

"""Define test fixtures for the AWSBraket HTTP client."""

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
    return 'arn:aws:braket:us-east-1:id:taskuuid'

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
def info():
    """Info value test setup."""
    return {
        'circuit': '{"braketSchemaHeader":'
        '{"name": "braket.ir.jaqcd.program", "version": "1"}, '
        '"results": [], "basis_rotation_instructions": [], '
        '"instructions": [{"target": 0, "type": "h"}, {\
            "target": 1, "type": "h"}, {\
                "control": 1, "target": 2, "type": "cnot"}]}',
        'nq': 10,
        'shots': 1,
        'backend': {'name': 'name2'},
    }

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
                "000": 0.1,
                "010": 0.4,
                "110": 0.1,
                "001": 0.1,
                "111": 0.3,
            },
            "measuredQubits": [0, 1, 2],
        }
    )

@pytest.fixture
def results_dict(results_json):
    """Results dict test setup."""
    body = StreamingBody(StringIO(results_json), len(results_json))
    return {
        'ResponseMetadata': {
            'RequestId': 'CF4CAA48CC18836C',
            'HTTPHeaders': {},
        },
        'Body': body,
    }

@pytest.fixture
def res_completed():
    """Completed results test setup."""
    return {"000": 0.1, "010": 0.4, "110": 0.1, "001": 0.1, "111": 0.3}

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
                "deviceName": "name3",
                "deviceType": "QPU",
                "deviceStatus": "ONLINE",
                "providerName": "pname2",
            },
            {
                "deviceArn": "invalid",
                "deviceName": "invalid",
                "deviceType": "BLABLA",
                "deviceStatus": "ONLINE",
                "providerName": "pname3",
            },
        ]
    }

@pytest.fixture
def device_value_devicecapabilities():
    """Device capabilities value test setup."""
    return json.dumps(
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

@pytest.fixture
def device_value(device_value_devicecapabilities):
    """Device value test setup."""
    return {
        "deviceName": "Aspen-8",
        "deviceType": "QPU",
        "providerName": "provider1",
        "deviceStatus": "OFFLINE",
        "deviceCapabilities": device_value_devicecapabilities,
    }

@pytest.fixture
def devicelist_result():
    """Device list value test setup."""
    return {
        'name1': {
            'coupling_map': {},
            'deviceArn': 'arn1',
            'location': 'us-east-1',
            'nq': 30,
            'version': '1',
            'deviceParameters': {
                'name': 'braket.device_schema.rigetti.rigetti_device_parameters',
                'version': '1',
            },
            'deviceModelParameters': {
                'name': 'braket.device_schema.gate_model_parameters',
                'version': '1',
            },
        },
        'name2': {
            'coupling_map': {'1': ['2', '3']},
            'deviceArn': 'arn2',
            'location': 'us-east-1',
            'nq': 30,
            'version': '1',
            'deviceParameters': {
                'name': 'braket.device_schema.rigetti.rigetti_device_parameters',
                'version': '1',
            },
            'deviceModelParameters': {
                'name': 'braket.device_schema.gate_model_parameters',
                'version': '1',
            },
        },
        'name3': {
            'coupling_map': {'1': ['2', '3']},
            'deviceArn': 'arn3',
            'location': 'us-east-1',
            'nq': 30,
            'version': '1',
            'deviceParameters': {
                'name': 'braket.device_schema.rigetti.rigetti_device_parameters',
                'version': '1',
            },
            'deviceModelParameters': {
                'name': 'braket.device_schema.gate_model_parameters',
                'version': '1',
            },
        },
    }

# ==============================================================================

@pytest.fixture
def show_devices_setup(creds, search_value, device_value, devicelist_result):
    """Show devices value test setup."""
    return creds, search_value, device_value, devicelist_result

@pytest.fixture
def retrieve_setup(arntask, creds, device_value, res_completed, results_dict):
    """Retrieve value test setup."""
    return arntask, creds, device_value, res_completed, results_dict

@pytest.fixture(params=["qpu", "sim"])
def retrieve_devicetypes_setup(request, arntask, creds, results_json, device_value_devicecapabilities):
    """Retrieve device types value test setup."""
    if request.param == "qpu":
        body_qpu = StreamingBody(StringIO(results_json), len(results_json))
        results_dict = {
            'ResponseMetadata': {
                'RequestId': 'CF4CAA48CC18836C',
                'HTTPHeaders': {},
            },
            'Body': body_qpu,
        }

        device_value = {
            "deviceName": "Aspen-8",
            "deviceType": "QPU",
            "providerName": "provider1",
            "deviceStatus": "OFFLINE",
            "deviceCapabilities": device_value_devicecapabilities,
        }

        res_completed = {"000": 0.1, "010": 0.4, "110": 0.1, "001": 0.1, "111": 0.3}
    else:
        results_json_simulator = json.dumps(
            {
                "braketSchemaHeader": {
                    "name": "braket.task_result.gate_model_task_result",
                    "version": "1",
                },
                "measurements": [
                    [0, 0],
                    [0, 1],
                    [1, 1],
                    [0, 1],
                    [0, 1],
                    [1, 1],
                    [1, 1],
                    [1, 1],
                    [1, 1],
                    [1, 1],
                ],
                "measuredQubits": [0, 1],
            }
        )
        body_simulator = StreamingBody(StringIO(results_json_simulator), len(results_json_simulator))
        results_dict = {
            'ResponseMetadata': {
                'RequestId': 'CF4CAA48CC18836C',
                'HTTPHeaders': {},
            },
            'Body': body_simulator,
        }

        device_value = {
            "deviceName": "SV1",
            "deviceType": "SIMULATOR",
            "providerName": "providerA",
            "deviceStatus": "ONLINE",
            "deviceCapabilities": device_value_devicecapabilities,
        }

        res_completed = {"00": 0.1, "01": 0.3, "11": 0.6}
    return arntask, creds, device_value, results_dict, res_completed

@pytest.fixture
def send_too_many_setup(creds, s3_folder, search_value, device_value):
    """Send too many value test setup."""
    info_too_much = {
        'circuit': '{"braketSchemaHeader":'
        '{"name": "braket.ir.jaqcd.program", "version": "1"}, '
        '"results": [], "basis_rotation_instructions": [], '
        '"instructions": [{"target": 0, "type": "h"}, {\
            "target": 1, "type": "h"}, {\
                "control": 1, "target": 2, "type": "cnot"}]}',
        'nq': 100,
        'shots': 1,
        'backend': {'name': 'name2'},
    }
    return creds, s3_folder, search_value, device_value, info_too_much

@pytest.fixture
def real_device_online_setup(
    arntask,
    creds,
    s3_folder,
    info,
    search_value,
    device_value,
    res_completed,
    results_json,
):
    """Real device online value test setup."""
    qtarntask = {'quantumTaskArn': arntask}
    body = StreamingBody(StringIO(results_json), len(results_json))
    results_dict = {
        'ResponseMetadata': {
            'RequestId': 'CF4CAA48CC18836C',
            'HTTPHeaders': {},
        },
        'Body': body,
    }

    return (
        qtarntask,
        creds,
        s3_folder,
        info,
        search_value,
        device_value,
        res_completed,
        results_dict,
    )

@pytest.fixture
def send_that_error_setup(creds, s3_folder, info, search_value, device_value):
    """Send error value test setup."""
    return creds, s3_folder, info, search_value, device_value