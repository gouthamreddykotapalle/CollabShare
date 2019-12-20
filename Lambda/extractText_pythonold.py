import json
import uuid
import base64
import boto3
import os
import sys
import io
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from google.cloud import vision
from google.cloud.vision import types

sys.path.insert(1, '/opt')
from dynamoUtility import persist_to_dynamo

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/google_cred.json"


def send_email(email_id, docName):
    print('contents of email for sendig OCR failure')
    client = boto3.client('ses', region_name='us-east-1')
    msg = """
    We regret to inform that your document upload to noteshare failed.
    Please try back in sometime.
    Document name: {0}""".format(str(docName))
    response = client.send_email(
        Destination={
            'ToAddresses': [email_id],
        },

        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': msg,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': 'Noteshare document upload',
            },
        },
        Source='sj3003@columbia.edu',
    )


def getTextFromOCR(image_path):
    client = vision.ImageAnnotatorClient()
    file_name = os.path.abspath(image_path)

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if not texts:
        return ""
    print("Output Text", texts[0].description)
    return texts[0].description


def saveTextToElastic(documentId, pageId, text):
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
    page = {
        "text": text,
        "comments": []
    }
    res = es.index(index="pages", doc_type="_doc", id=pageId, body=page)
    print("Elastic output", res)
    pass


def deleteDocFromQueue(message):
    client = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/285384211934/ocr-input-docs'
    response = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1
    )
    if 'Messages' in response:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']
        client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle)


def updateDynamoStatus(documentId, pageIds):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('documents')
    response = table.get_item(
        Key={
            "documentId": documentId
        }
    )
    document = response['Item']
    document['status'] = 'ACTIVE'
    table.put_item(Item=document)
    print("Document in dynamo now", document)

    table = dynamodb.Table('pages')
    for pageId in pageIds:
        response = table.get_item(
            Key={
                "pageId": pageId
            }
        )
        page = response['Item']
        page['status'] = 'ACTIVE'
        table.put_item(Item=page)
        print("Page in dynamo now for pageId", pageId)


def push_doc_to_queue(documentId, pageIds, count):
    msg = {"documentId": documentId,
           "pageIds": pageIds,
           "count": count
           }
    sqs = boto3.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='ocr-input-docs')
    print("sending to queue with count", count)
    q_resp = queue.send_message(MessageBody=json.dumps(msg))
    print("Sent to queue for documentId", documentId)


def lambda_handler(event, context):
    print("Printing event...")
    print(event)
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    doc = None
    if event['Records']:
        doc = deleteDocFromQueue(event['Records'][0]['body'])
    doc_str = event['Records'][0]['body']
    doc = json.loads(doc_str)
    count = 1
    failure = False
    if doc:
        print("inside processing unit", doc)
        count = doc['count']
        documentId = doc['documentId']
        pageIds = doc['pageIds']
        if (count == 5):
            ownerId = doc['ownerId']
            docTable = dynamodb.Table('documents')
            personsTable = dynamodb.Table('persons')
            docObj = docTable.get_item(
                Key={
                    "documentId": documentId
                })
            personObj = personsTable.get_item(
                Key={
                    "personId": ownerId
                })
            # send email to owner saying upload failed
            send_email(docObj['name'], personObj['email'])
            return  # returning as max retry over for this document

        for pageId in pageIds:
            print("processing for pageId ", pageId)
            image_name = str(pageId) + '.png'
            image_path = "/tmp/" + image_name
            s3.download_file("pages.noteshare", image_name, image_path)
            print("calling OCR for pageId", pageId)
            try:
                content = getTextFromOCR(image_path)
                print("Got content from OCR")
                print("Saving to elastic")
                saveTextToElastic(documentId, pageId, content)
                print("saved to elastic")
                # deal with OCR Failure
            except:
                failure = True
                print("OCR Failure")
                count = count + 1
                push_doc_to_queue(documentId, pageIds, count)

    if not failure:
        updateDynamoStatus(documentId, pageIds)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
