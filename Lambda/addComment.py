import json
import boto3
import uuid
import os
import sys
import time

sys.path.insert(1, '/opt')
from dynamoUtility import scan_dynamo, persist_to_dynamo
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def validateParameters(pageId, userId):
    # persons = scan_dynamo(personIds,'persons',['personId'],'personId')
    # rejected = personIds.copy()
    # accepted = []
    # for entry in persons:
    #         if entry['personId'] in personIds:
    #             rejected.remove(entry['personId'])
    #             accepted.append(entry['personId'])
    # return accepted, rejected
    pass


def addToElastic(pageId, commentId, comment, time_now):
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
    comment = {
        "text": comment,
        "timestamp": time_now,
    }
    es.update(index='pages', doc_type='_doc', id=pageId,
              body={
                  'doc': {'comments': {commentId: comment}}
              }
              )
    pass


def addToPagesCollection(pageId, commentId):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    pageTable = dynamodb.Table('pages')
    page = pageTable.get_item(Key={
        "pageId": pageId
    })
    page = page['Item']
    page['commentIds'].append(commentId)
    res = pageTable.put_item(Item=page)


def lambda_handler(event, context):
    # TODO implement
    # if  not validateParameters(event['pageId'],event['userId']):
    #     return {
    #     'statusCode': 401,
    #     'body': 'User unauthorized to access this page',
    #     'headers': {
    #         'Access-Control-Allow-Origin': "*",
    #         "Access-Control-Allow-Credentials": "true"
    #         }
    #     }

    commentId = str(uuid.uuid1())
    time_now = str(time.time())
    event = json.loads(event['body'])
    pageId = event['pageId']
    commentEntry = {
        "commentId": commentId,
        "pageId": pageId,
        "comment": event['comment'],
        "time": time_now,
        "userId": event['userId']
    }
    # add entry in comments
    persist_to_dynamo('comments', commentEntry)
    # update commentIds in pages
    addToPagesCollection(pageId, commentId)
    # add to elastic
    addToElastic(pageId, commentId, event['comment'], time_now)

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    peopleTable = dynamodb.Table('persons')
    person = peopleTable.get_item(Key={
        "personId": event['userId']
    })
    commentEntry['userName'] = person['Item']['name']

    return {
        'statusCode': 200,
        'body': json.dumps(commentEntry),
        'headers': {
            'Access-Control-Allow-Origin': "*",
            "Access-Control-Allow-Credentials": "true"
        }
    }
