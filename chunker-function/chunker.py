import os
from typing import Any, Dict, List
from uuid import uuid4

import boto3
from chromadb import ClientAPI, Collection, PersistentClient
from chunking_code.recursive_token_chunker import RecursiveTokenChunker
from chunking_code.utils import Language

CHROMA_DB_PATH: str = os.environ.get("CHROMA_DB_PATH")
COLLECTION_NAME: str = os.environ.get("COLLECTION_NAME")


def connectToDatabase() -> Collection:
    chroma_client: ClientAPI = PersistentClient(path=CHROMA_DB_PATH)
    collection: Collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME
    )
    return collection


def processChunks(collection: Collection, chunks: List[str]) -> None:
    ids: List[str] = [str(uuid4()) for _ in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)
    print("Length of chunks: ", len(chunks))
    print("Processed a message sucessfully")
    return None


def getChunks(text: str) -> List[str]:
    recursive_character_chunker: RecursiveTokenChunker = RecursiveTokenChunker(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=RecursiveTokenChunker.get_separators_for_language(Language.MARKDOWN),
    )

    return recursive_character_chunker.split_text(text=text)


def handler(event, context) -> Dict[str, Any]:

    ###########################################################################
    # This was written from the help of a youtube video
    # https://youtu.be/OJrxbr9ebDE?feature=shared
    # https://youtu.be/Q8OP_9V71GM?feature=shared
    ###########################################################################
    s3client = boto3.client(service_name="s3")

    # Get the bucket name
    bucket: str = event["Records"][0]["s3"]["bucket"]["name"]
    file_name: str = event["Records"][0]["s3"]["object"]["key"]
    print(f"Bucket: {bucket} | Key: {file_name}")

    # Get the file so we can process it
    print("INFO: Getting File Data")
    response = s3client.get_object(Bucket=bucket, Key=file_name)
    # Get the text and chunk it
    text: str = response["Body"].read().decode("utf-8")

    chunks: List[str] = getChunks(text=text)
    print(f"INFO: Received File Data. Now Sending it to the database")

    # Connect to the Chroma DB
    collection: Collection = connectToDatabase()

    # Process the chunks
    processChunks(collection=collection, chunks=chunks)

    return dict(
        statusCode=200, response="File chunked and added to the databse", error=None
    )
