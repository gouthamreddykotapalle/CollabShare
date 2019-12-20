import json
import boto3
import sys
from itertools import chain

sys.path.insert(1, '/opt')
from dynamoUtility import scan_dynamo


def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource("dynamodb")

    print(event)
    if event['queryStringParameters']['userID']:
        userId = event['queryStringParameters']['userID']
        attributes_to_get = ['userId', 'groupId']
        entry = scan_dynamo([userId], "persons", attributes_to_get, "personId")
        if entry:
            groups = entry[0]['groupId']
            attributes_to_get = ["documentIds"]
            docIds = scan_dynamo(groups, "groups", attributes_to_get, "groupId")
            docIds = [f["documentIds"] for f in docIds]
            docIds = list(set(list(chain(*docIds))))
            print(docIds)
        else:
            docIds = {}

    elif event['queryStringParameters']['groupID']:
        groupId = event['queryStringParameters']['groupID']
        attributes_to_get = ['documentIds']
        entry = scan_dynamo([groupId], "groups", attributes_to_get, "groupId")
        if entry:
            docIds = entry[0]['documentIds']
        else:
            docIds = []
        print(docIds)

    if docIds:
        docTable = dynamodb.Table("documents")
        attributes_to_get = ['documentId', 'name', 'description']
        documents = scan_dynamo(docIds, "documents", attributes_to_get, "documentId")
    else:
        documents = []

    return {
        'statusCode': 200,
        'body': json.dumps(documents),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
