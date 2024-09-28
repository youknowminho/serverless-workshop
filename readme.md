# Taylor Swift World Tour Ticketing System

Welcome to the **Taylor Swift World Tour Ticketing System** workshop project! This serverless application is designed to manage ticket sales, inventory, payments, and fan notifications for Taylor Swift's world tour events. Leveraging AWS Serverless technologies, this system ensures scalability, reliability, and cost-effectiveness, providing an excellent hands-on experience for AWS Serverless Cloud Engineers.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Components and Resources](#components-and-resources)
    - [DynamoDB Tables](#dynamodb-tables)
    - [SNS Topics and Subscriptions](#sns-topics-and-subscriptions)
    - [SQS Queues and Policies](#sqs-queues-and-policies)
    - [Lambda Functions](#lambda-functions)
    - [KMS Key](#kms-key)
    - [IAM Roles and Policies](#iam-roles-and-policies)
4. [Deployment Instructions](#deployment-instructions)
5. [Testing Guide](#testing-guide)
    - [Sample Payloads](#sample-payloads)
6. [Best Practices and Recommendations](#best-practices-and-recommendations)
7. [Conclusion](#conclusion)

---

## Project Overview

The **Taylor Swift World Tour Ticketing System** is a comprehensive serverless application built using AWS Serverless Application Model (SAM). It facilitates the entire ticketing process for concert events, including:

- **Ticket Purchases:** Handling user requests for buying tickets.
- **Inventory Management:** Tracking seat availability in real-time.
- **Payment Processing:** Managing transactions and applying discounts.
- **Fan Notifications:** Sending personalized updates and confirmations to fans.
- **Fan Club Rewards:** Distributing rewards to fan club members based on their purchases.

This project serves as an excellent workshop to understand and implement AWS serverless architectures, integrating various AWS services to build a cohesive and efficient system.

---

## Architecture Overview

![Architecture Diagram](./docs/architecture-diagram.png)

*Figure 1: High-Level Architecture of the Taylor Swift World Tour Ticketing System*

The architecture is designed using AWS Serverless components to ensure scalability, reliability, and security. Key elements include:

- **DynamoDB Tables:** For storing ticket, order, and fan club member data.
- **SNS Topics:** Facilitating event-driven communication between services.
- **SQS Queues:** Enabling asynchronous processing of events.
- **Lambda Functions:** Implementing business logic and processing events.
- **KMS Key:** Ensuring data encryption and security.
- **IAM Roles:** Managing permissions and access controls.

---

## Components and Resources

### DynamoDB Tables

#### 1. **SeatInventoryTable**

- **Purpose:** Tracks seat availability for each concert to prevent overbooking.
- **Key Attributes:**
  - `concertId` (HASH): Unique identifier for each concert.
  - `seatId` (RANGE): Unique identifier for each seat within a concert.
- **Billing Mode:** PAY_PER_REQUEST
- **Encryption:** Enabled via Server-Side Encryption (SSE) using AWS-managed keys.
- **Tags:** Project, Environment, Owner, auto-delete

#### 2. **OrdersTable**

- **Purpose:** Logs all ticket purchase orders, including user details and payment statuses.
- **Key Attributes:**
  - `orderId` (HASH): Unique identifier for each order.
- **Billing Mode:** PAY_PER_REQUEST
- **Encryption:** Enabled via SSE.
- **Tags:** Project, Environment, Owner, auto-delete

#### 3. **FanClubMembersTable**

- **Purpose:** Manages information about fan club members, facilitating personalized interactions and rewards.
- **Key Attributes:**
  - `fanClubId` (HASH): Unique identifier for each fan club member.
- **Billing Mode:** PAY_PER_REQUEST
- **Encryption:** Enabled via SSE.
- **Tags:** Project, Environment, Owner, auto-delete

### SNS Topics and Subscriptions

#### 1. **TourTicketingTopic**

- **Purpose:** Central hub for all ticketing-related events.
- **Properties:**
  - **TopicName:** `${Environment}-TourTicketingTopic`
  - **KmsMasterKeyId:** References `TicketingSystemKey` for encryption.
- **Tags:** Project, Environment, Owner, auto-delete

#### 2. **FanNotificationTopic**

- **Purpose:** Handles fan-specific notifications and communications.
- **Properties:**
  - **TopicName:** `${Environment}-FanNotificationTopic`
- **Tags:** Project, Environment, Owner, auto-delete

#### **SNS Subscriptions**

- **FanEmailSubscription:**
  - **Protocol:** `email`
  - **Endpoint:** Configured via `EmailAddress` parameter.
  - **Purpose:** Sends email confirmations to users upon ticket purchases.

- **SeatInventorySubscription, PaymentProcessingSubscription, NotificationSubscription, FanClubAwardsSubscription:**
  - **Protocol:** `sqs`
  - **Endpoint:** Respective SQS queue ARNs.
  - **Purpose:** Routes SNS topic messages to SQS queues for asynchronous processing.

### SQS Queues and Policies

#### 1. **SeatInventoryQueue**

- **Purpose:** Processes seat inventory updates asynchronously.
- **Properties:**
  - **QueueName:** `${Environment}-SeatInventoryQueue`
- **Tags:** Project, Environment, Owner, auto-delete

#### 2. **PaymentProcessingQueue**

- **Purpose:** Handles payment processing tasks.
- **Properties:**
  - **QueueName:** `${Environment}-PaymentProcessingQueue`
- **Tags:** Project, Environment, Owner, auto-delete

#### 3. **NotificationQueue**

- **Purpose:** Manages notification-related messages.
- **Properties:**
  - **QueueName:** `${Environment}-NotificationQueue`
- **Tags:** Project, Environment, Owner, auto-delete

#### 4. **FanClubAwardsQueue**

- **Purpose:** Processes fan club award distributions.
- **Properties:**
  - **QueueName:** `${Environment}-FanClubAwardsQueue`
- **Tags:** Project, Environment, Owner, auto-delete

#### **SQS Queue Policies**

Each SQS queue has an associated policy that grants the `TourTicketingTopic` permission to send messages, ensuring secure and authorized communication.

**Example: SeatInventoryQueuePolicy**
```yaml
SeatInventoryQueuePolicy:
  Type: AWS::SQS::QueuePolicy
  Properties:
    Queues:
      - !Ref SeatInventoryQueue
    PolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal: '*'
          Action: 'sqs:SendMessage'
          Resource: !GetAtt SeatInventoryQueue.Arn
          Condition:
            ArnEquals:
              aws:SourceArn: !Ref TourTicketingTopic
```

### Lambda Functions

#### 1. **TicketPurchaseHandlerFunction**

- **Purpose:** Handles ticket purchase events, updates DynamoDB tables, and publishes events to SNS topics.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `ticket_purchase_handler/`
- **Environment Variables:**
  - `SNS_TOPIC_ARN`: References `TourTicketingTopic`

#### 2. **SeatInventoryUpdaterFunction**

- **Purpose:** Updates seat inventory based on ticket purchases.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `seat_inventory_updater/`
- **Events:** Triggered by `SeatInventoryQueue`
- **Environment Variables:**
  - `DYNAMODB_TABLE_NAME`: References `SeatInventoryTable`

#### 3. **PaymentProcessorFunction**

- **Purpose:** Processes payments for ticket purchases.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `payment_processor/`
- **Events:** Triggered by `PaymentProcessingQueue`
- **Environment Variables:**
  - `DYNAMODB_TABLE_NAME`: References `OrdersTable`

#### 4. **FanNotifierFunction**

- **Purpose:** Sends notifications to fans upon ticket purchases and other events.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `fan_notifier/`
- **Events:** Triggered by `NotificationQueue`
- **Environment Variables:**
  - `SNS_TOPIC_ARN`: References `FanNotificationTopic`

#### 5. **FanClubAwardProcessorFunction**

- **Purpose:** Manages the distribution of fan club awards.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `fan_club_award_processor/`
- **Events:** Triggered by `FanClubAwardsQueue`
- **Environment Variables:**
  - `DYNAMODB_TABLE_NAME`: References `FanClubMembersTable`

#### 6. **PrintNotificationFunction**

- **Purpose:** Handles print notifications triggered by SNS events.
- **Handler:** `app.lambda_handler`
- **CodeUri:** `print_notification/`
- **Events:** Triggered by `TourTicketingTopic`
- **Environment Variables:** None

### KMS Key

#### **TicketingSystemKey**

- **Purpose:** Encrypts sensitive data, particularly SNS topics.
- **Key Policy:**
  - Grants administrative permissions to the account root.
  - Allows `TicketPurchaseHandlerRole` to perform decryption and generate data keys.
- **Tags:** Project, Environment, Owner, auto-delete

### IAM Roles and Policies

Each Lambda function is assigned an IAM role that defines its permissions to interact with other AWS services.

#### 1. **TicketPurchaseHandlerRole**

- **Permissions:** 
  - `sns:Publish` to `TourTicketingTopic`
  - Basic Lambda execution permissions.

#### 2. **SeatInventoryUpdaterRole**

- **Permissions:** 
  - `dynamodb:UpdateItem` on `SeatInventoryTable`
  - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `SeatInventoryQueue`
  - Basic Lambda execution permissions.

#### 3. **PaymentProcessorRole**

- **Permissions:** 
  - `dynamodb:PutItem` on `OrdersTable`
  - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `PaymentProcessingQueue`
  - Basic Lambda execution permissions.

#### 4. **FanNotifierRole**

- **Permissions:** 
  - `sns:Publish` to `FanNotificationTopic`
  - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `NotificationQueue`
  - Basic Lambda execution permissions.

#### 5. **FanClubAwardProcessorRole**

- **Permissions:** 
  - `dynamodb:UpdateItem` on `FanClubMembersTable`
  - `sqs:ReceiveMessage`, `sqs:DeleteMessage`, `sqs:GetQueueAttributes` on `FanClubAwardsQueue`
  - Basic Lambda execution permissions.

#### 6. **PrintNotificationRole**

- **Permissions:** 
  - Basic Lambda execution permissions.

---

## Deployment Instructions

Deploying the **Taylor Swift World Tour Ticketing System** involves building and deploying the SAM template to your AWS account. Follow these steps to get started:

### Prerequisites

Ensure you have the following tools installed and configured:

- **AWS CLI:** [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS SAM CLI:** [Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- **Git:** Optional, for version control.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo/taylor-swift-ticketing-system.git
cd taylor-swift-ticketing-system
```

### Step 2: Build the Application

```bash
sam build
```

- **What It Does:**
  - Installs dependencies for each Lambda function.
  - Compiles code if necessary.
  - Prepares deployment artifacts.

### Step 3: Deploy the Application

```bash
sam deploy --capabilities CAPABILITY_NAMED_IAM --guided
```

- **`--capabilities CAPABILITY_NAMED_IAM`:** Grants SAM permission to create or modify IAM roles with custom names.
- **`--guided`:** Launches an interactive setup to configure deployment settings.

**Deployment Prompts:**

- **Stack Name:** Default is `taylor-swift-ticketing-stack`.
- **AWS Region:** Choose your preferred region.
- **Parameters:** Set values for `Environment`, `OwnerAlias`, `EmailAddress`, and `SpringClean`.
- **Review Changes:** Confirm changes before deployment.
- **IAM Role Creation:** Allow SAM to create necessary IAM roles.
- **Rollback Settings:** Decide whether to disable rollback on deployment failure.
- **Save Configuration:** Optionally save deployment settings for future use.

### Step 4: Verify Deployment

- **CloudFormation Console:** Check the deployed stack and its resources.
- **AWS SAM Outputs:** Retrieve resource identifiers and endpoints from the `Outputs` section.
- **Testing Resources:**
  - **Lambda Functions:** Test via the AWS Lambda Console or using event triggers.
  - **SNS Topics and SQS Queues:** Publish messages and verify routing and processing.
  - **DynamoDB Tables:** Insert and retrieve items to ensure functionality.

---

## Testing Guide

Testing is crucial to ensure that each component of the system functions correctly and interacts seamlessly with other services. This guide provides an overview of how to test each Lambda function by modifying code and configurations, along with sample payloads for comprehensive testing.

### Overview of Lambda Functions

1. **PrintNotificationFunction:** Logs SNS messages to CloudWatch for auditing.
2. **TicketPurchaseHandlerFunction:** Processes ticket purchases, updates DynamoDB, and publishes SNS events.
3. **FanClubAwardProcessorFunction:** Updates fan club member rewards based on purchases.
4. **FanNotifierFunction:** Sends personalized notifications to fans.
5. **PaymentProcessorFunction:** Handles payment processing and applies discounts.
6. **SeatInventoryUpdaterFunction:** Updates seat availability in DynamoDB.

### General Testing Approaches

- **Modifying Lambda Code:** Enhance logging, introduce conditional logic, and simulate errors.
- **Adjusting Configuration Settings:** Change environment variables, memory allocations, and IAM policies.
- **Utilizing Diverse Payloads:** Use varied JSON payloads to test different scenarios, including edge cases.

### Suggestions for Testing Each Lambda Function

#### PrintNotificationFunction

- **Modify Logging:** Add timestamps or additional metadata to logs.
- **Handle New Attributes:** Extend the function to process additional message attributes.
- **Error Simulation:** Introduce intentional parsing errors to test error handling.

#### TicketPurchaseHandlerFunction

- **Modify Order ID Generation:** Change the method to ensure uniqueness and compliance.
- **Adjust Membership Logic:** Alter criteria for fan club membership to test discount applications.
- **Simulate High Load:** Test the function's performance under multiple simultaneous purchase requests.
- **Extend Data Processing:** Add new fields to purchase details and verify SNS publication.

#### FanClubAwardProcessorFunction

- **Change Reward Points:** Adjust the number of points awarded to test DynamoDB updates.
- **Handle Multiple Members:** Process messages containing multiple fan club members.
- **Introduce Conditional Awards:** Implement tiered reward systems based on membership levels.
- **Enhance Error Handling:** Manage scenarios with non-existent fan club IDs.

#### FanNotifierFunction

- **Customize Notification Templates:** Alter message formats to include additional information.
- **Test Different Message Contents:** Use varied payloads to ensure correct message formatting.
- **Integrate with Other Services:** Extend notifications to SMS or mobile push notifications.
- **Performance Optimization:** Experiment with batching messages to improve throughput.

#### PaymentProcessorFunction

- **Adjust Discount Rates:** Change discount percentages to observe impacts on total amounts.
- **Simulate Payment Failures:** Introduce logic to randomly fail payments and test graceful handling.
- **Integrate with Real Payment Gateways:** Replace simulated processing with actual integrations.
- **Validate Data Integrity:** Ensure all necessary fields are correctly stored in DynamoDB.

#### SeatInventoryUpdaterFunction

- **Toggle Seat Availability:** Change availability statuses based on different conditions.
- **Bulk Updates:** Test handling of large batches of seat updates.
- **Concurrency Handling:** Assess how the function manages simultaneous updates to the same seat.
- **Implement Seat Locking:** Add logic to temporarily lock seats during purchase processing.

### Sample Payloads

#### 1. **Basic Ticket Purchase**

```json
{
  "body": "{\n  \"concertName\": \"Reputation Tour\",\n  \"concertDate\": \"2024-12-05\",\n  \"tickets\": [\n    {\n      \"seatClass\": \"Standard\",\n      \"seatSection\": \"B\",\n      \"seatRow\": \"10\",\n      \"seatNumber\": \"15\",\n      \"isFanClubMember\": false\n    }\n  ],\n  \"totalAmount\": 100.00\n}"
}
```

#### 2. **Fan Club Member Ticket Purchase**

```json
{
  "body": "{\n  \"concertName\": \"Lover Fest\",\n  \"concertDate\": \"2024-11-15\",\n  \"tickets\": [\n    {\n      \"seatClass\": \"Premium\",\n      \"seatSection\": \"C\",\n      \"seatRow\": \"5\",\n      \"seatNumber\": \"20\",\n      \"isFanClubMember\": true\n    }\n  ],\n  \"totalAmount\": 150.00\n}"
}
```

#### 3. **Multiple Ticket Purchase with Mixed Membership**

```json
{
  "body": "{\n  \"concertName\": \"Fearless Tour\",\n  \"concertDate\": \"2024-09-18\",\n  \"tickets\": [\n    {\n      \"seatClass\": \"Standard\",\n      \"seatSection\": \"D\",\n      \"seatRow\": \"12\",\n      \"seatNumber\": \"22\",\n      \"isFanClubMember\": false\n    },\n    {\n      \"seatClass\": \"VIP\",\n      \"seatSection\": \"A\",\n      \"seatRow\": \"1\",\n      \"seatNumber\": \"1\",\n      \"isFanClubMember\": true\n    }\n  ],\n  \"totalAmount\": 250.00\n}"
}
```

#### 4. **VIP Ticket Purchase**

```json
{
  "body": "{\n  \"concertName\": \"1989 Tour\",\n  \"concertDate\": \"2024-10-10\",\n  \"tickets\": [\n    {\n      \"seatClass\": \"VIP\",\n      \"seatSection\": \"A\",\n      \"seatRow\": \"1\",\n      \"seatNumber\": \"1\",\n      \"isFanClubMember\": true\n    }\n  ],\n  \"totalAmount\": 300.00\n}"
}
```

#### 5. **Edge Case: Malformed JSON Payload**

```json
{
  "body": "{\n  \"concertName\": \"Reputation Tour\",\n  \"concertDate\": \"2024-12-05\",\n  \"tickets\": \"invalid_ticket_format\",\n  \"totalAmount\": \"one hundred\"\n}"
}
```

#### 6. **Edge Case: Missing Required Fields**

```json
{
  "body": "{\n  \"tickets\": [\n    {\n      \"seatClass\": \"Standard\",\n      \"seatSection\": \"E\",\n      \"seatRow\": \"8\",\n      \"seatNumber\": \"18\",\n      \"isFanClubMember\": false\n    }\n  ],\n  \"totalAmount\": 80.00\n}"
}
```

#### 7. **Edge Case: Invalid Data Types**

```json
{
  "body": "{\n  \"concertName\": \"Lover Fest\",\n  \"concertDate\": \"2024-11-15\",\n  \"tickets\": [\n    {\n      \"seatClass\": \"Premium\",\n      \"seatSection\": \"F\",\n      \"seatRow\": \"7\",\n      \"seatNumber\": \"35\",\n      \"isFanClubMember\": \"yes\"\n    }\n  ],\n  \"totalAmount\": \"two hundred\"\n}"
}
```

### How to Use These Payloads

1. **Local Testing with AWS SAM CLI:**
   - **Step 1:** Save each payload as a separate JSON file (e.g., `basic_purchase.json`, `fan_club_purchase.json`).
   - **Step 2:** Invoke the Lambda function locally using SAM CLI:
     ```bash
     sam local invoke TicketPurchaseHandlerFunction --event events/basic_purchase.json
     ```
   - **Step 3:** Observe the function's behavior and output in the terminal and logs.

2. **Deploying and Testing in AWS:**
   - **Step 1:** Use AWS Console or AWS CLI to send these payloads to the deployed Lambda function.
   - **Step 2:** Monitor **CloudWatch Logs** to verify processing.

---

## Best Practices and Recommendations

- **Isolate Testing Environments:** Use separate environments (e.g., dev, test, prod) to prevent interference between tests and production data.
- **Automate Testing:** Implement automated tests to ensure consistent and repeatable validation.
- **Comprehensive Logging:** Ensure all Lambda functions have detailed logging for monitoring and debugging.
- **Principle of Least Privilege:** Assign only necessary permissions to IAM roles to enhance security.
- **Monitor Performance Metrics:** Use AWS CloudWatch and X-Ray to monitor function performance and identify bottlenecks.
- **Handle Exceptions Gracefully:** Implement robust error handling within Lambda functions to manage unexpected scenarios without disrupting workflows.

---

## Conclusion

The **Taylor Swift World Tour Ticketing System** provides a comprehensive example of building a scalable and secure serverless application using AWS technologies. By following this ReadMe, AWS Serverless Cloud Engineers can effectively deploy, test, and optimize the system, gaining valuable insights into serverless architecture best practices.

Engage with the system by:

- **Exploring the Architecture:** Understand how different AWS services interact to form a cohesive ticketing system.
- **Modifying Lambda Functions:** Enhance or extend business logic to accommodate new features or requirements.
- **Conducting Thorough Testing:** Utilize diverse payloads and testing strategies to ensure system robustness and reliability.
- **Implementing Best Practices:** Adhere to security, performance, and cost optimization guidelines to maintain an efficient and secure application.

---

*Happy Deploying and Testing! 🎟️🎤*


