import boto3


# this will be added as a layer to functions using it

def scan_dynamo(ids, tableName, attributes_to_get, primaryKey):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)
    response = table.scan(
        AttributesToGet=attributes_to_get,
        ScanFilter={primaryKey: {
            'AttributeValueList': ids,
            'ComparisonOperator': 'IN'
        }
        }
    )
    return response['Items']


def persist_to_dynamo(tableName, body):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tableName)
    table.put_item(
        Item=body
    )
