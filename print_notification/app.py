import json

def lambda_handler(event, context):
    for record in event['Records']:
        # Extract the SNS message
        sns_message = record['Sns']['Message']
        sns_subject = record['Sns'].get('Subject', 'No Subject')
        sns_attributes = record['Sns'].get('MessageAttributes', {})

        # Print message details to CloudWatch Logs
        print("Received message from TourTicketingTopic:")
        print(f"Subject: {sns_subject}")
        print("Message Attributes:")
        for attr_key, attr_value in sns_attributes.items():
            print(f"  {attr_key}: {attr_value['Value']}")
        print("Message Content:")
        print(sns_message)
        print("-" * 60)

    return {
        'statusCode': 200,
        'body': json.dumps('Notifications printed successfully')
    }
