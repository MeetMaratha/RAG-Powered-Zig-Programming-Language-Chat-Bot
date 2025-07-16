import json
import os
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from chromadb import Collection, PersistentClient, QueryResult

CHROMA_DB_PATH: str = os.environ.get("CHROMA_DB_PATH")
COLLECTION_NAME: str = os.environ.get("COLLECTION_NAME")


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
    return secret["generate-response-sqs-queue-url"]


def pushDataToQueue(
    processing_id: str, query: str, documents: Dict[str, Dict[str, Dict[str, str]]]
) -> None:
    sqs_client = boto3.client(service_name="sqs", region_name="us-east-1")
    payload: str = json.dumps(
        {"processing_id": processing_id, "query": query, **documents}
    )

    print("Payload is: ", payload)

    sqs_client.send_message(QueueUrl=getQueueLink(), MessageBody=payload)

    return None


def connectToDatabase() -> Collection:
    chroma_client: PersistentClient = PersistentClient(path=CHROMA_DB_PATH)
    try:
        collection: Collection = chroma_client.get_collection(name=COLLECTION_NAME)
    except Exception:
        print(f"We are most probably not able to get collection {COLLECTION_NAME}")
        return None
    return collection


def getVector(
    collection: Collection, query: str, number_of_relevant_vectors: int = 5
) -> Dict[str, Dict[str, Dict[str, str]]]:
    documents: QueryResult = collection.query(
        query_texts=[query], n_results=number_of_relevant_vectors
    )

    # Safely get first query results (empty lists if missing)
    ids: List[str] = documents.get("ids", [[]])[0] or []
    docs: List[str] = documents.get("documents", [[]])[0] or []
    metas: List[Dict[str, Any]] = documents.get("metadatas", [[]])[0] or []

    # Create result dictionary
    return {
        "documents": {
            id: {"document": doc, "metadata": meta}
            for id, doc, meta in zip(ids, docs, metas)
        }
    }


def handler(event, context) -> Dict[str, Any]:

    collection: Optional[Collection] = connectToDatabase()
    if collection is None:
        return dict(statusCode=500, error="The vector database is missing")
    try:
        body: Dict[str, str] = json.loads(
            event.get("Records")[0]["body"].replace("'", '"')
        )
        print(type(body))
        print(body)
        query: str = body.get("query")
        number_of_relevant_vectors: int = int(body.get("number_of_relevant_vectors", 5))
        processing_id: str = body.get("processing_id")
    except Exception:
        print("Some values were not provided")
        return dict(
            statusCode=422,
            error="One of the required parameter 'query' or 'number_of_relevant_vectors' is missing",
        )

    print("Query is: ", query)
    print("Processing ID is: ", processing_id)
    print("Number of Relevant Vectors to find: ", number_of_relevant_vectors)

    pushDataToQueue(
        query=query,
        processing_id=processing_id,
        documents=getVector(
            collection=collection,
            query=query,
            number_of_relevant_vectors=number_of_relevant_vectors,
        ),
    )

    return dict(
        statusCode=200,
        response="Sent the data for further processing",
        error=None,
    )
