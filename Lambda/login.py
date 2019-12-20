import json
import boto3
import sys

sys.path.insert(1, '/opt')
from dynamoUtility import persist_to_dynamo, scan_dynamo


def checkIfExist(personId):
    persons = scan_dynamo([personId], 'persons', ['personId'], 'personId')
    if persons:
        return True
    return False


def lambda_handler(event, context):
    # The event structure is described below
    # Pre sign up handler should put all necessary information onto dynamoDB
    """
        event {
    	'version': '1',
    	'region': 'us-east-1',
    	'userPoolId': 'us-east-1_rpUsHwFI1',
    	'userName': 'Google_115313088983646160901',
    	'callerContext': {
    		'awsSdkVersion': 'aws-sdk-unknown-unknown',
    		'clientId': '1962ro47nqjq5nreds0et30e6a'
    	},
    	'triggerSource': 'PreSignUp_ExternalProvider',
    	'request': {
    		'userAttributes': {
    			'cognito:email_alias': '',
    			'cognito:phone_number_alias': '',
    			'given_name': 'shashank',
    			'email': 'shashank93jai@gmail.com'
    		},
    		'validationData': {}
    	},
    	'response': {
    		'autoConfirmUser': False,
    		'autoVerifyEmail': False,
    		'autoVerifyPhone': False
    	}
    }"""
    if not checkIfExist(event['userName']):
        personInfo = {
            "personId": event['userName'],
            "name": event['request']['userAttributes']['given_name'],
            "email": event['request']['userAttributes']['email'],
            "groupId": []
        }
        persist_to_dynamo('persons', personInfo)

    # DO NOT CHANGE, Cognito requires event to be returned to complete successful sign up
    return event
