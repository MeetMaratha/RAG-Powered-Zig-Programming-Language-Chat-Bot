import json
from typing import Dict

import boto3
import requests


def processMessage(message: Dict) -> None:
    PROCESSING_LAMBDA_FUNCTION_URL: str = (
        "http://generate-response:8080/2015-03-31/functions/function/invocations"
    )

    message_body: Dict = json.loads(message.get("Body"))
    print("Message Body while making generate-response event driven:")
    print(message_body)

    requests.post(
        url=PROCESSING_LAMBDA_FUNCTION_URL,
        json={
            "query": message_body.get("query"),
            "processing_id": message_body.get("processing_id"),
        },
    )

    print(
        f"Sent Query request: {message_body.get('query')} with Processing ID: {message_body.get('processing_id')} to {PROCESSING_LAMBDA_FUNCTION_URL}"
    )


if __name__ == "__main__":
    sqs_client = boto3.client(
        service_name="sqs",
        endpoint_url="http://elastic-mq:9324",
        region_name="elasticmq",
        aws_access_key_id="XXXX",
        aws_secret_access_key="XXXX",
    )
    QUEUE_URL: str = "http://elastic-mq:9324/000000000000/submit-request-queue"

    while True:
        response = sqs_client.receive_message(
            QueueUrl=QUEUE_URL, MaxNumberOfMessages=10, WaitTimeSeconds=20
        )

        if "Messages" in response:
            for message in response["Messages"]:
                print(f"Processing Message: {message["ReceiptHandle"]}")
                processMessage(message=message)
                sqs_client.delete_message(
                    QueueUrl=QUEUE_URL, ReceiptHandle=message["ReceiptHandle"]
                )
