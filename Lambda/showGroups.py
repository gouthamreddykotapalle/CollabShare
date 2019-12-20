import json
import boto3
import sys

sys.path.insert(1, '/opt')
from dynamoUtility import scan_dynamo


def lambda_handler(event, context):
    # TODO implement

    requesterId = event['queryStringParameters']['q']
    dynamodb = boto3.resource('dynamodb')
    personTable = dynamodb.Table('persons')

    person = personTable.get_item(Key={
        "personId": requesterId
    })
    if 'Item' not in person:
        return {
            'statusCode': 400,
            'body': 'Invalid personId'
        }
    groupIds = person['Item']['groupId']
    print("GroupIds received from person table")
    print(groupIds)
    groups_info = []
    if groupIds:
        groupTable = dynamodb.Table('groups')
        groups_info = scan_dynamo(groupIds, 'groups', ['description', 'groupName', 'owner', 'groupId'], 'groupId')

    return {
        'statusCode': 200,
        'body': json.dumps(groups_info),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
