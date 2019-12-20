##### DO
##### NOT
##### RUN
##### TESTS

# TESTS HAVE BEEN CAREFULLY CONFIGURED TO IMITATE BEHAVIOR. RECORDS ARE ACTUALLY REMOED- IF YOU RUN A SECOND TIME, ERRORS WILL TURN UP

import json
import boto3


def lambda_handler(event, context):
    print(event)
    groupId = event['queryStringParameters']['groupId']

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    groupTable = dynamodb.Table('groups')
    group = groupTable.get_item(Key={
        "groupId": groupId
    })['Item']
    print(group)
    '''
    group entry:
    {
        "groupID": groupId
        "description": descreption
        "documentIds": [docIds]
        "groupName": groupName
        "owner" : owner
        "people": [people]
    }
    '''

    # remove document dependencies from group, delete document if not assocaited to any group post removal
    docTable = dynamodb.Table('documents')
    cascade_flag = 0
    '''
    for docId in group['documentIds']:
        print(docId)
        doc = docTable.get_item( Key = {
            "documentId" : docId
        })['Item']
        #if groupId in doc['groupIds']:  # line not needed- consistency to be maintained- document is in group only if group has document
        doc['groupIds'] = doc['groupIds'].remove(groupId)
        if not doc['groupIds']:
            #delete from pages tabe and corresponding s3 image
            s3 = boto3.client('s3')
            pageTable = dynamodb.Table('pages')
            for pageId in doc['pageIds']:
                print(pageId)
                pageTable.delete_item(Key = {
                    "pageId" : pageId
                })
                s3.delete_object(Bucket='pages.noteshare', Key=str(pageId)+".png")
            #delete from documents table
            res = docTable.delete_item(Key = {
                "documentId" : docId
            })
            cascade_flag = 1
        else:
            res = docTable.put_item(Item=doc)
    '''
    # remove group from everybody's list
    userTable = dynamodb.Table("persons")
    usersToDeleteGroupFrom = group['people']
    print(groupId)
    print("Users t delete from: ", usersToDeleteGroupFrom)
    for person in usersToDeleteGroupFrom:
        print("person: ", person)
        user = userTable.get_item(Key={
            "personId": person
        })['Item']

        user['groupId'].remove(groupId)
        print(user['groupId'])
        res = userTable.put_item(Item=user)
    print("Person table association removed")

    # remove group from groups table
    res = groupTable.delete_item(Key={
        "groupId": groupId
    })
    print("Group deleted, cascade_flag = ", cascade_flag)

    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Group deletion successful, cascad'),
        'headers': {
            "Access-Control-Allow-Origin": "*",
        }
    }
