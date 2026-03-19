import boto3
import json
from boto3.dynamodb.conditions import Key

# AWS Service Client
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Translations")


def lambda_handler(event, context):
    try:

        # Request Logging
        print("Received event:", json.dumps(event))

        # Authentication: Extract user identity from Cognito JWT token
        user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
        print(f"Authenticated user: {user_id}")

        # Database Query: Retrieve translation history for the user
        print("Querying DynamoDB for translation history")

        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False  # newest first
        )

        items = response.get("Items", [])

        print(f"Retrieved {len(items)} translation records")

        # Successful API Response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(items)
        }

    except Exception as e:

        # Error Handling and Logging
        print("Lambda execution error:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps("Server error")
        }