import json
import boto3


def lambda_handler(event, context):
    # TODO implement
    print('event', event)
    if "documentId" in event["pathParameters"].keys():
        documentId = event['pathParameters']['documentId']

        dynamo = boto3.resource("dynamodb")
        docTable = dynamo.Table("documents")
        pageIds = docTable.get_item(Key={
            "documentId": documentId
        })['Item']['pageIds']

        pageTable = dynamo.Table("pages")

        pages = []
        for pageId in pageIds:
            page = pageTable.get_item(Key={
                "pageId": pageId
            })['Item']

            comments = page['commentIds']
            url = page['url']
            pages.append({"pageId": pageId, "commentIds": comments, "url": url})
        return {
            'statusCode': 200,
            'body': json.dumps({"documentId": documentId, "pages": pages}),
            'headers': {
                "Access-Control-Allow-Origin": "*",
            }
        }

    else:
        documentId = "Invalid"
        pages = []
        return {
            'statusCode': 400,
            'body': json.dumps("Invalid document Id"),
            'headers': {
                "Access-Control-Allow-Origin": "*",
            }
        }
