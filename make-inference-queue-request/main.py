import json
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError


def getQueueLink():

    secret_name = "prod/queue-secrets"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response["SecretString"])
    return secret["start-response-sqs-queue-url"]


def handler(event, context) -> Dict[str, Any]:

    try:
        print("Raw event:", event)

        # Extract body (API Gateway sends it as string)

        # Get parameters
        query: str = event.get("query")
        uuid: str = event.get("uuid")

        print(f"Query: {query}, UUID: {uuid}")

        if not query or not uuid:
            raise ValueError("Both 'query' and 'uuid' must be provided")

        sqs_client = boto3.client(
            service_name="sqs",
            region_name="us-east-1",
        )
        sqs_client.send_message(
            QueueUrl=getQueueLink(),
            MessageBody=json.dumps({"query": query, "processing_id": uuid}),
        )

        # Correct response format for API Gateway proxy integration
        return dict(
            statusCode=200,
            response="The response generation has been started. You can start querying the dynamodb for the response.",
        )

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return dict(
            statusCode=400,
            error=str(e),
        )
