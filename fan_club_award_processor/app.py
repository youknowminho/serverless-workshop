import json
import boto3
import os

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ['DYNAMODB_TABLE_NAME']
    table = dynamodb.Table(table_name)

    for record in event['Records']:
        try:
            # Parse the message body from SQS
            message_body = record['body']
            message = json.loads(message_body)
            tickets = message['tickets']
            for ticket in tickets:
                if ticket.get('isFanClubMember', False):
                    fan_club_id = ticket['fanClubId']
                    # Update fan club member rewards
                    table.update_item(
                        Key={'fanClubId': fan_club_id},
                        UpdateExpression="ADD rewardPoints :points",
                        ExpressionAttributeValues={':points': 100}
                    )
        except Exception as e:
            print(f"Error updating fan club rewards: {e}")

