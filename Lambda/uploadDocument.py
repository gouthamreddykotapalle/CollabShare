import json
import uuid
import base64
import boto3
import sys
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

sys.path.insert(1, '/opt')
from dynamoUtility import persist_to_dynamo

s3_base_url = 'https://s3.amazonaws.com/pages.noteshare/'


def saveToElastic(documentId, name, description):
    host = 'search-noteshare-khiicienqkujyqqz7vm4mmbwzm.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    client = boto3.client('es')
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    document = {
        "description": description,
        "name": name
    }
    es.index(index="documents", doc_type="_doc", id=documentId, body=document)
    # response = es.search(index='photos')
    pass


def persist_to_documents(event, pageIds):
    document = {
        "documentId": event['documentID'],
        "name": event['documentName'],
        "ownerId": event['ownerId'],
        "description": event['description'],
        "groupIds": event['groupIds'],
        "pageIds": pageIds,
        "status": "DRAFT"
    }

    persist_to_dynamo('documents', document)
    print("Persisted to documents for documentId", event['documentID'])


def persist_to_pages(documentId, index, pageId, image_name):
    page = {
        "pageId": pageId,
        "pageNumber": index,
        "url": s3_base_url + image_name,
        "documentId": documentId,
        "commentIds": [],
        "status": "DRAFT"
    }
    persist_to_dynamo('pages', page)
    print("Persisted to pages for pageId", pageId)


def push_doc_to_queue(documentId, pageIds, ownerId):
    # pageImageMap = dict(zip(pageIds, contents))
    msg = {"documentId": documentId,
           "pageIds": pageIds,
           "count": 1,
           "ownerId": ownerId
           }
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='ocr-input-docs')
    print("sending to queue")
    q_resp = queue.send_message(MessageBody=json.dumps(msg))
    print("Sent to queue for documentId", documentId)


def updateGroupsTable(documentId, groupIds):
    dynamodb = boto3.resource("dynamodb")
    groupTable = dynamodb.Table("groups")
    for groupId in groupIds:
        group = groupTable.get_item(Key={
            "groupId": groupId
        })['Item']
        group['documentId'] = group['documentIds'].append(documentId)
        groupTable.put_item(Item=group)


def lambda_handler(event, context):
    print(event)
    documentId = event['documentID']
    groupIds = event['groupIds']
    pageIds = []
    for i in range(event['noOfPages']):
        pageId = documentId + '_' + str(i)
        pageIds.append(pageId)
        persist_to_pages(documentId, i, pageId, pageId + '.png')

    # persist to documentCollection
    persist_to_documents(event, pageIds)

    # save document to elastic
    saveToElastic(documentId, event['documentName'], event['description'])

    # add document to groups
    updateGroupsTable(documentId, groupIds)

    # push the image content to queue SQS with the doc_ID stamped
    push_doc_to_queue(documentId, pageIds, event['ownerId'])

    return {
        'statusCode': 200,
        'body': json.dumps({"documentID": documentId,
                            "pageIds": pageIds
                            }),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
