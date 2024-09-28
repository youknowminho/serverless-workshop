import json
import boto3
import uuid
import datetime
import os

def lambda_handler(event, context):
    sns = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']

    try:
        # Check if 'body' key exists in event (e.g., from API Gateway)
        if 'body' in event:
            purchase_details = json.loads(event['body'])
        else:
            purchase_details = event

        # Add orderId and purchaseTimestamp
        purchase_details['orderId'] = str(uuid.uuid4())
        purchase_details['purchaseTimestamp'] = datetime.datetime.utcnow().isoformat() + 'Z'

        # Determine if any tickets are for fan club members
        has_fan_club_member = any(
            ticket.get('isFanClubMember', False) for ticket in purchase_details['tickets']
        )

        # Publish the message to SNS Topic with message attribute
        response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps(purchase_details),
            MessageAttributes={
                'hasFanClubMember': {
                    'DataType': 'String',
                    'StringValue': str(has_fan_club_member).lower()
                }
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Purchase processed successfully',
                'orderId': purchase_details['orderId']
            })
        }
    except Exception as e:
        print(f"Error processing purchase: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }

