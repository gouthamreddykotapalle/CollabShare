import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    groupId = event['queryStringParameters']['groupId']
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    groupTable = dynamodb.Table('groups')
    group = groupTable.get_item(Key={
        "groupId": groupId
    })
    owner = group['Item']['owner']
    peopleIds = group['Item']['people']
    peopleTable = dynamodb.Table('persons')
    persons = []
    res = {}
    for peopleId in peopleIds:
        entry = peopleTable.get_item(Key={
            "personId": peopleId
        })
        persons.append(entry)
    res = {
        "ownerId": owner,
        "persons": persons
    }
    return {
        'statusCode': 200,
        'body': json.dumps(res),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
