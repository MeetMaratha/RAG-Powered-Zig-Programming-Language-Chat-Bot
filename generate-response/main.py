import json
from datetime import datetime

import boto3
import requests

TABLE_NAME: str = "response-table"


def processEvent(query: str, processing_id: str) -> None:
    print("Processing ID: ", processing_id)
    print("Message: ", query)
    try:
        # Your existing processing logic
        data = {"query": query, "number_of_relevant_documents": 5}
        response = requests.post(
            "http://chroma-db-fetcher:8000/get_relevant_vectors",
            json=data,
        )

        if response.ok:
            documents = response.json()["documents"]
            context_list = [doc["document"] for doc in documents.values()]

            inference_response = requests.post(
                "http://inference-model:8000/get_inference",
                json={"query": query, "context": context_list},
            )

            if inference_response.ok:
                result = inference_response.json()["response"]
                # Store result
                dynamodb = boto3.client(
                    service_name="dynamodb",
                    endpoint_url="http://dynamo-db:8000",
                    region_name="elasticmq",
                    aws_access_key_id="XXXX",
                    aws_secret_access_key="XXXX",
                )
                dynamodb.put_item(
                    Item={
                        "processing_id": {"S": processing_id},
                        "status": {"S": "COMPLETED"},
                        "result": {"S": result},
                        "timestamp": {"S": datetime.utcnow().isoformat()},
                    },
                    TableName=TABLE_NAME,
                    ReturnConsumedCapacity="TOTAL",
                )
            else:
                dynamodb = boto3.client(
                    service_name="dynamodb",
                    endpoint_url="http://dynamo-db:8000",
                    region_name="elasticmq",
                    aws_access_key_id="XXXX",
                    aws_secret_access_key="XXXX",
                )
                dynamodb.put_item(
                    Item={
                        "processing_id": {"S": processing_id},
                        "status": {"S": "ERROR"},
                        "error": {
                            "S": f"Inference failed: {inference_response.status_code}"
                        },
                    },
                    TableName=TABLE_NAME,
                    ReturnConsumedCapacity="TOTAL",
                )
        else:
            dynamodb = boto3.client(
                service_name="dynamodb",
                endpoint_url="http://dynamo-db:8000",
                region_name="elasticmq",
                aws_access_key_id="XXXX",
                aws_secret_access_key="XXXX",
            )
            dynamodb.put_item(
                Item={
                    "processing_id": {"S": processing_id},
                    "status": {"S": "ERROR"},
                    "error": {"S": f"Vector lookup failed: {response.status_code}"},
                },
                TableName=TABLE_NAME,
                ReturnConsumedCapacity="TOTAL",
            )

    except Exception as e:
        dynamodb = boto3.client(
            service_name="dynamodb",
            endpoint_url="http://dynamo-db:8000",
            region_name="elasticmq",
            aws_access_key_id="XXXX",
            aws_secret_access_key="XXXX",
        )
        dynamodb.put_item(
            Item={
                "processing_id": {"S": processing_id},
                "status": {"S": "ERROR"},
                "error": {"S": str(e)},
            },
            TableName=TABLE_NAME,
            ReturnConsumedCapacity="TOTAL",
        )


def handler(event, context):

    query: str = event.get("query")
    processing_id: str = event.get("processing_id")
    print(
        f"INFO: Query passed: {query} | Processing ID: {processing_id} in Generate Response Function"
    )
    processEvent(query=query, processing_id=processing_id)

    # This is the original one


#     for record in event["Records"]:
#         message = json.loads(record["body"])
#         processing_id = message["uuid"]
#         query = message["query"]
