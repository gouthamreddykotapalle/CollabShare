import json
import boto3
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

stackOverflowBaseUrl = "https://api.stackexchange.com/2.2/search/advanced?order=desc&sort=activity&site=stackoverflow"
from os import sys

sys.path.insert(1, '/opt')
from dynamoUtility import scan_dynamo


def getStackOverflowResults(text):
    url = stackOverflowBaseUrl + "&q=" + text + "&pagesize=" + str(5)
    response = requests.get(url)
    data = response.json()
    data = data['items']
    links = []
    for entry in data:
        links.append(entry['link'])
    return links


def getElasticClient():
    # es.indices.delete(index='test-index', ignore=[400, 404])
    service = 'es'
    host = 'search-noteshare-khiicienqkujyqqz7vm4mmbwzm.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
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
    return es


def search_elastic(search_body, index):
    es = getElasticClient()
    print("Search body ", search_body)
    response = es.search(index=index, body=search_body)
    print("elastic response is ", response)
    print("Response= ", response)
    if 'hits' in response['hits']:
        return response['hits']['hits']
    else:
        return []


def getDocSearchBody(documentIds, queryString):
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": queryString,
                            # "default_field": "text"
                        }
                    }
                ],
                "filter": [{"terms": {"_id": documentIds}}]
            }
        }
    }
    return search_body


def getPageSearchBody(pageIds, queryString):
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": queryString,
                            # "default_field": "text"
                        }
                    }
                ],
                "filter": [{"terms": {"_id": pageIds}}]
            }
        }
    }
    return search_body


# not fully working
def getAccessIds(userId):
    attributes_to_get = ['personId', 'groupId']
    entry = scan_dynamo([userId], "persons", attributes_to_get, "personId")
    groups = entry[0]['groupId']
    print(groups)
    if not groups:
        return [], []

    attributes_to_get = ['documentIds']
    entry = scan_dynamo(groups, "groups", attributes_to_get, "groupId")
    print(entry)
    docIdListofLists = [doc['documentIds'] for doc in entry]
    docIds = [docId for sublist in docIdListofLists for docId in sublist]
    print("Document Ids: ", docIds)
    if not docIds:
        return [], []
    attributes_to_get = ['pageIds']
    entry = scan_dynamo(docIds, "documents", attributes_to_get, "documentId")
    pageIdListofLists = [page['pageIds'] for page in entry]
    pageIds = [pageId for sublist in pageIdListofLists for pageId in sublist]
    print("PageIds: ", pageIds)

    return docIds, pageIds


def lambda_handler(event, context):
    # TODO implement
    queryString = event['queryStringParameters']['q']
    userId = event['queryStringParameters']['userID']

    print("UserId: ", userId)
    documentIds, pageIds = getAccessIds(userId)

    links = getStackOverflowResults(queryString)
    doc_search_body = getDocSearchBody(documentIds, queryString)
    print("documentSearchBody is ", doc_search_body)
    documents_res = search_elastic(doc_search_body, "documents")
    documentObjs = []
    pageObjs = []

    for entry in documents_res:
        documentObjs.append({
            "documentId": entry['_id'],
            "documentName": entry['_source']['name']
        })

    page_search_body = getPageSearchBody(pageIds, queryString)
    print("pageSearchBody is ", page_search_body)
    pages_res = search_elastic(page_search_body, "pages")
    print("Page results: ", pages_res)

    pageIdsRes = []
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    pageTable = dynamodb.Table('pages')
    docTable = dynamodb.Table('documents')
    for entry in pages_res:
        page = pageTable.get_item(Key={
            "pageId": entry['_id']
        })
        page = page['Item']
        docId = page['documentId']
        doc = docTable.get_item(Key={
            "documentId": docId
        })
        pageObjs.append({
            "pageId": entry['_id'],
            "documentName": doc['Item']['name']
        })

    res = {
        "documents": documentObjs,
        "pages": pageObjs,
        "stackOverflowLinks": links
    }

    return {
        'statusCode': 200,
        'body': json.dumps(res),
        'headers': {
            'Access-Control-Allow-Origin': "*",
            "Access-Control-Allow-Credentials": "true"
        }

    }
