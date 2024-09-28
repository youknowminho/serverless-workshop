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
            concert_id = message['concertId']
            for ticket in tickets:
                seat_id = f"{ticket['seatSection']}-{ticket['seatRow']}-{ticket['seatNumber']}"
                # Update seat availability in DynamoDB
                table.update_item(
                    Key={
                        'concertId': concert_id,
                        'seatId': seat_id
                    },
                    UpdateExpression="SET isAvailable = :val",
                    ExpressionAttributeValues={
                        ':val': False
                    }
                )
        except Exception as e:
            print(f"Error updating seat inventory: {e}")

