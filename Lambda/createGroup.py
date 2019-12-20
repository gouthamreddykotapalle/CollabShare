import json
import boto3
import uuid
import os
import sys

sys.path.insert(1, '/opt')
from dynamoUtility import scan_dynamo, persist_to_dynamo


def validatePersonsByEmailIds(emailIds):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('persons')
    print("emailds", emailIds)
    persons = table.scan(
        ScanFilter={'email': {
            'AttributeValueList': emailIds,
            'ComparisonOperator': 'IN'
        }
        }
    )
    print("persons", persons)
    if 'Items' not in persons:
        return [], emailIds
    persons = persons['Items']
    rejectedEmail = emailIds.copy()
    acceptedUsers = []
    for entry in persons:
        if entry['email'] in emailIds:
            rejectedEmail.remove(entry['email'])
            acceptedUsers.append(entry['personId'])
    print("Accepted User: ", acceptedUsers)
    print("Rejected User:", rejectedEmail)
    return acceptedUsers, rejectedEmail


def addGroupToAcceptedPersons(accepted, groupId):
    dynamodb = boto3.resource('dynamodb')
    personTable = dynamodb.Table('persons')
    for id in accepted:
        person = personTable.get_item(Key={
            "personId": id
        })['Item']
        print(person)
        person['groupId'].append(groupId)
        person = personTable.put_item(Item=person)


def lambda_handler(event, context):
    body = json.loads(event['body'])
    print("body", body)
    emailIds = body['emailIds']
    emailIds.append(body['ownerEmailID'])
    acceptedUsers, rejectedEmails = validatePersonsByEmailIds(emailIds)
    print("accepted")
    print(acceptedUsers)
    groupId = str(uuid.uuid1())
    print(groupId)
    addGroupToAcceptedPersons(acceptedUsers, groupId)
    if not body['description']:
        body['description'] = " "

    groupEntry = {
        "groupId": groupId,
        "groupName": body['groupName'],
        "description": body['description'],
        "owner": body['ownerID'],
        "people": acceptedUsers,
        "documentIds": []
    }
    persist_to_dynamo('groups', groupEntry)

    return {
        'statusCode': 200,
        'body': json.dumps(groupEntry),
        'headers': {
            'Access-Control-Allow-Origin': "*",
            "Access-Control-Allow-Credentials": "true"
        }
    }
