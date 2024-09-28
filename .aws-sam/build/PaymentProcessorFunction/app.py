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
            total_amount = message['totalAmount']
            is_fan_club_member = any(
                ticket.get('isFanClubMember', False) for ticket in tickets
            )

            # Apply discount if fan club member
            if is_fan_club_member:
                discount_rate = 0.10  # 10% discount
                total_amount *= (1 - discount_rate)
                message['totalAmount'] = total_amount

            # Simulate payment processing (replace with actual payment gateway integration)
            payment_successful = True  # Assume payment is successful for simulation

            # Update payment status
            message['paymentStatus'] = 'Completed' if payment_successful else 'Failed'

            # Store order details in DynamoDB
            table.put_item(Item=message)
        except Exception as e:
            print(f"Error processing payment: {e}")

