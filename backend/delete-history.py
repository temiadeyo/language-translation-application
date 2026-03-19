import boto3
import json

# AWS Service Client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Translations')


def lambda_handler(event, context):
    try:

        # Request Logging
        print("Received event:", json.dumps(event))

        # Authentication: Extract user identity from Cognito JWT token
        user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
        print(f"Authenticated user: {user_id}")

        # Request Parsing: Extract timestamp from path parameters
        timestamp = event["pathParameters"]["id"]
        print(f"Delete request received for timestamp: {timestamp}")

        # Database Operation: Delete translation record
        print("Deleting record from DynamoDB")

        table.delete_item(
            Key={
                "user_id": user_id,
                "timestamp": timestamp
            }
        )

        print(f"Record deleted for user {user_id} at timestamp {timestamp}")

        # Successful API Response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({"message": "Deleted successfully"})
        }

    except Exception as e:

        # Error Handling and Logging
        print("Lambda execution error:", str(e))

        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps("Server error")
        }