import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    groupId = event['pathParameters']['groupId']
    print(groupId)
    body = json.loads(event['body'])
    print(body)
    email = body['email']

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    personTable = dynamodb.Table('persons')
    persons = personTable.scan(
        ScanFilter={'email': {
            'AttributeValueList': [email],
            'ComparisonOperator': 'IN'
        }
        }
    )
    print(persons)
    if 'Items' not in persons:
        return {
            'statusCode': 404,
            'body': json.dumps('User not in noteshare yet')
        }

    person = persons['Items'][0]
    userId = person['personId']
    person['groupId'].append(groupId)
    res = personTable.put_item(Item=person)

    groupTable = dynamodb.Table('groups')

    group = groupTable.get_item(Key={
        "groupId": groupId
    })['Item']

    group['people'].append(userId)
    ownerId = group['owner']
    print(ownerId)

    res = groupTable.put_item(Item=group)
    print(" Users added")

    returnMsg = {"ownerId": ownerId, "person": person}

    return {
        'statusCode': 200,
        'body': json.dumps(returnMsg),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
