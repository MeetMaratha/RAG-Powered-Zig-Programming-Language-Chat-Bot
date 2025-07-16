import json
import os

import boto3


def handler(event, context):
    try:
        # Get UUID from query parameters
        uuid = event.get("uuid")

        if not uuid:
            return dict(statusCode=400, error="No UUID provided")

        dynamo_db_client = boto3.client(
            service_name="dynamodb",
            region_name="us-east-1",
        )
        # Get item from DynamoDB
        response = dynamo_db_client.get_item(
            Key={"processing_id": {"S": uuid}}, TableName=os.getenv(key="TABLE_NAME")
        )

        if "Item" not in response:
            return dict(statusCode=404, error="Result not found")

        result = response["Item"].get("result", "Processing").get("S")

        return dict(
            statusCode=200,
            response=result,
        )

    except Exception as e:
        print(e)
        return dict(statusCode=500, error=str(e))
