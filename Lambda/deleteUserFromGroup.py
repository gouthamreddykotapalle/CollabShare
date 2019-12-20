import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    print('event', event);
    groupId = event['pathParameters']['groupId']
    userId = event['pathParameters']['userid']
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    groupTable = dynamodb.Table('groups')
    entry = groupTable.get_item(Key={
        "groupId": groupId
    })
    entry = entry['Item']
    entry['people'].remove(userId)
    res = groupTable.put_item(Item=entry)

    personTable = dynamodb.Table('persons')
    entry = personTable.get_item(Key={
        "personId": userId
    })
    entry = entry['Item']
    entry['groupId'].remove(groupId)
    res = personTable.put_item(Item=entry)

    # usersToRemove = event['body']['users']
    # group['people'] = [i for i in group['people'] if i not in usersToRemove ]

    print(" Users removed")

    return {
        'statusCode': 200,
        'body': json.dumps('Task  successful'),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
