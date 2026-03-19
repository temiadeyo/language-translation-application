import boto3
import json
from datetime import datetime

# AWS service clients
translate = boto3.client('translate')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Translations')

# Supported language mapping for Amazon Translate
language_codes = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Japanese": "ja"
}

# Maximum allowed input text length
max_text_length = 1000


def lambda_handler(event, context):
    try:

        # Request Logging
        print("Received event:", json.dumps(event))

        # Authentication: Extract user identity from Cognito JWT token
        user_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
        print(f"Authenticated user: {user_id}")

        # Request Parsing: Extract request body parameters
        body = json.loads(event.get("body", "{}"))
        text_original = body.get("text_original", "").strip()
        language = body.get("language")

        print(f"Translation request received. Target language: {language}")

        # Input Validation
        if not text_original:
            print("Validation error: text is empty")
            return response(400, "Text is required")

        if len(text_original) > max_text_length:
            print("Validation error: text exceeds maximum length")
            return response(400, f"Text must be under {max_text_length} characters")

        if language not in language_codes:
            print(f"Validation error: unsupported language {language}")
            return response(400, "Unsupported language")

        # Translation Processing (Amazon Translate)
        print("Calling Amazon Translate service")

        translated_response = translate.translate_text(
            Text=text_original,
            SourceLanguageCode="auto",
            TargetLanguageCode=language_codes[language]
        )

        text_translated = translated_response["TranslatedText"]

        print("Translation successful")

        # Data Persistence (Store translation in DynamoDB)
        timestamp = datetime.utcnow().isoformat()

        table.put_item(
            Item={
                "user_id": user_id,
                "timestamp": timestamp,
                "originalText": text_original,
                "translatedText": text_translated,
                "language": language
            }
        )

        print(f"Translation stored in DynamoDB for user {user_id} at {timestamp}")

        # Successful API Response
        return response(200, {"translatedText": text_translated})

    except Exception as e:

        # Error Handling and Logging
        print("Lambda execution error:", str(e))
        return response(500, "Server error")


# API Response Formatter
def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }