import json
import boto3
import os

def lambda_handler(event, context):
    sns = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']

    for record in event['Records']:
        try:
            # Parse the message body from SQS
            message_body = record['body']
            message = json.loads(message_body)

            # Compose the notification message
            concert_name = message.get('concertName', 'Concert')
            concert_date = message.get('concertDate', 'Date')
            tickets_info = message.get('tickets', [])
            total_amount = message.get('totalAmount', 0.0)
            ticket_details = ''
            for ticket in tickets_info:
                seat_class = ticket.get('seatClass', 'Unknown')
                seat_section = ticket.get('seatSection', 'Unknown')
                seat_row = ticket.get('seatRow', 'Unknown')
                seat_number = ticket.get('seatNumber', 'Unknown')
                ticket_details += f"- {seat_class} Seat: Section {seat_section}, Row {seat_row}, Seat {seat_number}\n"

            notification_message = (
                f"Dear Fan,\n\n"
                f"Thank you for your purchase!\n\n"
                f"Concert: {concert_name}\n"
                f"Date: {concert_date}\n"
                f"Tickets:\n{ticket_details}\n"
                f"Total Amount: ${total_amount:.2f}\n\n"
                f"Enjoy the show!\n\n"
                f"Best regards,\n"
                f"Taylor Swift Ticketing Team"
            )

            # Publish the notification to SNS topic
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=notification_message
            )
        except Exception as e:
            print(f"Error sending notification: {e}")

