import json
import sys
import boto3

sys.path.insert(1, '/opt')
from dynamoUtility import persist_to_dynamo, scan_dynamo


def lambda_handler(event, context):
    pageId = event['queryStringParameters']['q']
    dynamodb = boto3.resource("dynamodb")
    docTable = dynamodb.Table("comments")
    attributes_to_get = ['comment', 'time', 'userId']
    comment_val = scan_dynamo([pageId], "comments", attributes_to_get, "pageId")

    peopleTable = dynamodb.Table('persons')
    for entry in comment_val:
        person = peopleTable.get_item(Key={
            "personId": entry['userId']
        })
        entry['userName'] = person['Item']['name']

    comment_val.sort(key=lambda x: x['time'], reverse=False)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(comment_val),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
