# -*- coding: utf-8 -*-

# Copyright 2016-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in 
# compliance with the License. A copy of the License is located at
# 
#     http://aws.amazon.com/asl/
# 
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific 
# language governing permissions and limitations under the License.

import logging
import httplib
import re
import sys
import time
from validation import validateResponse, validateContext

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SAMPLE_MANUFACTURER = 'Sample Manufacturer'
SAMPLE_APPLIANCES = [
    {
        'applianceId': 'Switch-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Switch',
        'version': '1',
        'friendlyName': 'Switch',
        'friendlyDescription': 'On/off switch that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'Dimmer-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Dimmer',
        'version': '1',
        'friendlyName': 'Upstairs Dimmer',
        'friendlyDescription': 'Dimmer that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
            'setPercentage',
            'incrementPercentage',
            'decrementPercentage',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'Fan-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Fan',
        'version': '1',
        'friendlyName': 'Upstairs Fan',
        'friendlyDescription': 'Fan that is functional and reachable',
        'isReachable': True,
        'actions': [
            'turnOn',
            'turnOff',
            'setPercentage',
            'incrementPercentage',
            'decrementPercentage',
        ],
        'additionalApplianceDetails': {}        
    },
    {
        'applianceId': 'SwitchUnreachable-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Switch',
        'version': '1',
        'friendlyName': 'Switch Unreachable',
        'friendlyDescription': 'Switch that is unreachable and shows (Offline)',
        'isReachable': False,
        'actions': [
            'turnOn',
            'turnOff',
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatAuto-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Family Room',
        'friendlyDescription': 'Thermostat in AUTO mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatHeat-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Guestroom',
        'friendlyDescription': 'Thermostat in HEAT mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatCool-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Hallway',
        'friendlyDescription': 'Thermostat in COOL mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatEco-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Kitchen',
        'friendlyDescription': 'Thermostat in ECO mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatCustom-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Laundry Room',
        'friendlyDescription': 'Thermostat in CUSTOM mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'ThermostatOff-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Thermostat',
        'version': '1',
        'friendlyName': 'Living Room',
        'friendlyDescription': 'Thermostat in OFF mode and reachable',
        'isReachable': True,
        'actions': [
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature',
            'getTargetTemperature',
            'getTemperatureReading',            
        ],
        'additionalApplianceDetails': {}
    },
    {
        'applianceId': 'Lock-001',
        'manufacturerName': SAMPLE_MANUFACTURER,
        'modelName': 'Lock',
        'version': '1',
        'friendlyName': 'Door',
        'friendlyDescription': 'Lock that is functional and reachable',
        'isReachable': True,
        'actions': [
            'setLockState',
            'getLockState',
        ],
        'additionalApplianceDetails': {}
    },
]

def lambda_handler(event,context):
    try:
        validateContext(context)

        logger.info('Request Header:{}'.format(event['header']))
        logger.info('Request Payload:{}'.format(event['payload']))

        response = {}
        if event['header']['namespace'] == 'Alexa.ConnectedHome.Discovery':
            response = handleDiscovery(event,context)      
        elif event['header']['namespace'] in ['Alexa.ConnectedHome.Control','Alexa.ConnectedHome.Query']:
            response = handleControl(event,context)

        logger.info('Response Header:{}'.format(response['header']))
        logger.info('Response Payload:{}'.format(response['payload']))

        validateResponse(event,response)     
        
        return response
    except ValueError as error:
        logger.error(error)
        raise
        
def handleDiscovery(event,context):
    response_name = 'DiscoverAppliancesResponse'
    header = generateResponseHeader(event,response_name)
    payload = {
       'discoveredAppliances': SAMPLE_APPLIANCES + generateSampleErrorAppliances()
    }
    response = generateResponse(header,payload)
    return response

def handleControl(event,context):
    payload = {}
    appliance_id = event['payload']['appliance']['applianceId']
    message_id = event['header']['messageId']
    request_name = event['header']['name']

    response_name = ''

    previous_temperature = 21.0
    minimum_temperature = 5.0
    maximum_temperature = 30.0

    if appliance_id == 'ThermostatAuto-001':
        previous_mode = 'AUTO'
        target_mode = 'AUTO'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatHeat-001':
        previous_mode = 'HEAT'
        target_mode = 'HEAT'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)
    
    elif appliance_id == 'ThermostatCool-001':
        previous_mode = 'COOL'
        target_mode = 'COOL'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatEco-001':
        previous_mode = 'ECO'
        target_mode = 'ECO'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatCustom-001':
        previous_mode = 'CUSTOM'
        target_mode = 'CUSTOM'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'ThermostatOff-001':
        previous_mode = 'OFF'
        target_mode = 'OFF'
        response = generateTemperatureResponse(event,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature)

    elif appliance_id == 'Lock-001':
        if request_name == 'SetLockStateRequest':
            response_name = 'SetLockStateConfirmation'
            payload = {
                'lockState': event['payload']['lockState']
            }

        elif request_name == 'GetLockStateRequest':
            response_name = 'GetLockStateResponse'
            payload = {
                'lockState': 'UNLOCKED',
                'applianceResponseTimestamp': getUTCTimestamp()
            }
        header = generateResponseHeader(event,response_name)
        response = generateResponse(header,payload)

    elif isSampleErrorAppliance(appliance_id):
        response_name = appliance_id.replace('-001','')
        header = generateResponseHeader(event,response_name)
        payload = {}
        if response_name == 'ValueOutOfRangeError':
            payload = {
                'minimumValue': 5.0,
                'maximumValue': 30.0,
            }
        elif response_name == 'DependentServiceUnavailableError':
            payload = {
                'dependentServiceName': 'Customer Credentials Database',
            }
        elif response_name == 'TargetFirmwareOutdatedError' or response_name == 'TargetBridgeFirmwareOutdatedError':
            payload = {
                'minimumFirmwareVersion': '17',
                'currentFirmwareVersion': '6',
            }
        elif response_name.startswith('UnableToGetValueError') or response_name.startswith('UnableToSetValueError'):
            if response_name.startswith('UnableToGetValueError'):
                code = response_name.replace('UnableToGetValueError-','')
                header['namespace'] = 'Alexa.ConnectedHome.Query'
                header['name'] = 'UnableToGetValueError'
            else:
                code = response_name.replace('UnableToSetValueError-','')
                header['name'] = 'UnableToSetValueError'
            payload = {
                'errorInfo': {
                    'code': code,
                    'description': 'The requested operation cannot be completed because the device is ' + code,
                }
            }
            
        elif response_name == 'UnwillingToSetValueError':
            payload = {
                'errorInfo': {
                    'code': 'ThermostatIsOff',
                    'description': 'The requested operation is unsafe because it requires changing the mode.',
                }
            }
        elif response_name == 'RateLimitExceededError':
            payload = {
                'rateLimit': '10',
                'timeUnit': 'HOUR',
            }
        elif response_name == 'NotSupportedInCurrentModeError':
            payload = {
                'currentDeviceMode': 'AWAY',
            }
        elif response_name == 'UnexpectedInformationReceivedError':
            payload = {
                'faultingParameter': 'value',
            }

        response = generateResponse(header,payload)

    else:

        if request_name == 'TurnOnRequest': response_name = 'TurnOnConfirmation'
        if request_name == 'TurnOffRequest': response_name = 'TurnOffConfirmation'
        if request_name == 'SetTargetTemperatureRequest': 
            response_name = 'SetTargetTemperatureConfirmation'
            target_temperature = event['payload']['targetTemperature']['value']
            payload = {
                'targetTemperature': {
                    'value': target_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                },
                'previousState' : {
                    'targetTemperature':{
                        'value': 21.0
                    },
                    'temperatureMode':{
                        'value': 'AUTO'
                    }
                }
            }
        if request_name == 'IncrementTargetTemperatureRequest':
            response_name = 'IncrementTargetTemperatureConfirmation'
            delta_temperature = event['payload']['deltaTemperature']['value']
            payload = {
                'previousState': {
                    'temperatureMode': {
                        'value': 'AUTO'
                    },
                    'targetTemperature': {
                        'value': 21.0
                    }
                },
                'targetTemperature': {
                    'value': 21.0 + delta_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                }
            }        
        if request_name == 'DecrementTargetTemperatureRequest':
            response_name = 'DecrementTargetTemperatureConfirmation'
            delta_temperature = event['payload']['deltaTemperature']['value']
            payload = {
                'previousState': {
                    'temperatureMode': {
                        'value': 'AUTO'
                    },
                    'targetTemperature': {
                        'value': 21.0
                    }
                },
                'targetTemperature': {
                    'value': 21.0 - delta_temperature
                },
                'temperatureMode': {
                    'value': 'AUTO'
                }
            }        
        if request_name == 'SetPercentageRequest': response_name = 'SetPercentageConfirmation'
        if request_name == 'IncrementPercentageRequest': response_name = 'IncrementPercentageConfirmation'
        if request_name == 'DecrementPercentageRequest': response_name = 'DecrementPercentageConfirmation'
        
        if appliance_id == 'SwitchUnreachable-001':
            response_name = 'TargetOfflineError'
    
        header = generateResponseHeader(event,response_name)
        response = generateResponse(header,payload)

    return response

# utility functions
def generateSampleErrorAppliances():
    # this should be in sync with same list in validation.py
    VALID_CONTROL_ERROR_RESPONSE_NAMES = [
        'ValueOutOfRangeError',
        'TargetOfflineError',
        'BridgeOfflineError',
        'NoSuchTargetError',
        'DriverInternalError',
        'DependentServiceUnavailableError',
        'TargetConnectivityUnstableError',
        'TargetBridgeConnectivityUnstableError',
        'TargetFirmwareOutdatedError',
        'TargetBridgeFirmwareOutdatedError',
        'TargetHardwareMalfunctionError',
        'TargetBridgeHardwareMalfunctionError',
        'UnableToGetValueError',
        'UnableToSetValueError',
        'UnwillingToSetValueError',
        'RateLimitExceededError',
        'NotSupportedInCurrentModeError',
        'ExpiredAccessTokenError',
        'InvalidAccessTokenError',
        'UnsupportedTargetError',
        'UnsupportedOperationError',
        'UnsupportedTargetSettingError',
        'UnexpectedInformationReceivedError'
    ]
    sample_error_appliances = []
    
    device_number = 1

    for error in VALID_CONTROL_ERROR_RESPONSE_NAMES:
        if error in ['UnableToGetValueError','UnableToSetValueError']:
            VALID_UNABLE_ERROR_INFO_CODES = [
                'DEVICE_AJAR',
                'DEVICE_BUSY',
                'DEVICE_JAMMED',
                'DEVICE_OVERHEATED',
                'HARDWARE_FAILURE',
                'LOW_BATTERY',
                'NOT_CALIBRATED'
            ]
            for code in VALID_UNABLE_ERROR_INFO_CODES:
                friendly_name = generateErrorFriendlyName(device_number) + ' door'
                if error == 'UnableToGetValueError':
                    friendly_description = 'Utterance: Alexa, is ' + friendly_name + ' locked? Response: ' + error + ' code: ' + code    
                else:
                    friendly_description = 'Utterance: Alexa, lock ' + friendly_name + '. Response: ' + error + ' code: ' + code    

                sample_error_appliance = {
                    'applianceId': error + '-' + code + '-001',
                    'manufacturerName': SAMPLE_MANUFACTURER,
                    'modelName': 'Lock',
                    'version': '1',
                    'friendlyName': friendly_name,
                    'friendlyDescription': friendly_description,
                    'isReachable': True,
                    'actions': [
                        'setLockState',
                        'getLockState',                        
                    ],
                    'additionalApplianceDetails': {}
                }

                sample_error_appliances.append(sample_error_appliance)
                device_number = device_number + 1

        else:
            friendly_name = generateErrorFriendlyName(device_number)
            friendly_description = 'Utterance: Alexa, turn on ' + friendly_name + '. Response: ' + error    

            sample_error_appliance = {
                'applianceId': error + '-001',
                'manufacturerName': SAMPLE_MANUFACTURER,
                'modelName': 'Switch',
                'version': '1',
                'friendlyName': friendly_name,
                'friendlyDescription': friendly_description,
                'isReachable': True,
                'actions': [
                    'turnOn',
                    'turnOff',                        
                ],
                'additionalApplianceDetails': {}
            }

            if error == 'ValueOutOfRangeError':
                sample_error_appliance['friendlyDescription'] = 'Utterance: Alexa, set ' + friendly_name + ' to 80 degrees. Response: ' + error
                sample_error_appliance['modelName'] = 'Thermostat'
                sample_error_appliance['actions'] = [
                    'setTargetTemperature',
                    'incrementTargetTemperature',
                    'decrementTargetTemperature',
                ]

            sample_error_appliances.append(sample_error_appliance)
            device_number = device_number + 1

    return sample_error_appliances

def isSampleErrorAppliance(appliance_id):
    sample_error_appliances = generateSampleErrorAppliances()
    for sample_error_appliance in sample_error_appliances:
        if sample_error_appliance['applianceId'] == appliance_id: return True
    return False

def generateResponseHeader(request,response_name):
    header = {
        'namespace': request['header']['namespace'],
        'name': response_name,
        'payloadVersion': '2',
        'messageId': request['header']['messageId'],        
    }
    return header

def generateResponse(header,payload):
    response = {
        'header': header,
        'payload': payload,
    }
    return response

def generateTemperatureResponse(request,previous_temperature,previous_mode,target_mode,minimum_temperature,maximum_temperature):
    request_name = request['header']['name']
    message_id = request['header']['messageId']
    
    # valid request    
    if request_name in ['SetTargetTemperatureRequest','IncrementTargetTemperatureRequest','DecrementTargetTemperatureRequest']:
        if request_name == 'SetTargetTemperatureRequest': 
            response_name = 'SetTargetTemperatureConfirmation'
            target_temperature = request['payload']['targetTemperature']['value']
        if request_name == 'IncrementTargetTemperatureRequest':
            response_name = 'IncrementTargetTemperatureConfirmation'
            target_temperature = previous_temperature + request['payload']['deltaTemperature']['value']
        if request_name == 'DecrementTargetTemperatureRequest':
            response_name = 'DecrementTargetTemperatureConfirmation'
            target_temperature = previous_temperature - request['payload']['deltaTemperature']['value']

        payload = {
            'targetTemperature': {
                'value': target_temperature
            },
            'temperatureMode': {
                'value': target_mode
            },
            'previousState' : {
                'targetTemperature':{
                    'value': previous_temperature
                },
                'temperatureMode':{
                    'value': previous_mode
                }
            }        
        }
    elif request_name == 'GetTemperatureReadingRequest':
        response_name = 'GetTemperatureReadingResponse'
        payload = {
            'temperatureReading': {
                'value': 21.00,
            }
        }

    elif request_name == 'GetTargetTemperatureRequest':
        response_name = 'GetTargetTemperatureResponse'
        payload = {
            'applianceResponseTimestamp': getUTCTimestamp(),
            'temperatureMode': {
                'value': target_mode,
                'friendlyName': '',
            }
        }

        if target_mode in ['HEAT','COOL','ECO','CUSTOM']:
            payload['targetTemperature'] = {
                'value': 21.00,
            }
        elif target_mode in ['AUTO']:
            payload['coolingTargetTemperature'] = {
                'value': 23.00
            }
            payload['heatingTargetTemperature'] = {
                'value': 19.00
            }

        if target_mode == 'CUSTOM':
            payload['temperatureMode']['friendlyName'] = 'Manufacturer custom mode'


    else:
        response_name = 'UnexpectedInformationReceivedError'
        payload = {
            'faultingParameter': 'request.name: ' + request_name
        }

    header = generateResponseHeader(request,response_name)
    response = generateResponse(header,payload)
    return response

def generateErrorFriendlyName(device_number):
    return 'Device ' + str(device_number)


"""Utility functions."""

def getUTCTimestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))
