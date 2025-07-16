import json
import os
import signal
import subprocess
import sys
import time
from threading import Timer
from typing import Dict, List, Optional, Tuple

import boto3
import requests
from langchain_ollama import OllamaLLM

SERVER_STARTED: bool = False
OLLAMA_HOST: str = "http://localhost:11434"
MODEL_NAME = os.getenv(key="MODEL_NAME")
EFS_PATH = os.getenv(key="EFS_PATH")
TABLE_NAME = os.getenv(key="TABLE_NAME")


def start_ollama_server():
    global SERVER_STARTED
    if SERVER_STARTED:
        return True
    try:
        # Start server redirecting output to Lambda's stdout/stderr
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=sys.stdout,  # Directly print stdout
            stderr=sys.stderr,  # Directly print stderr
            preexec_fn=os.setsid,
            text=True,  # Ensure output as text (Python 3.7+)
        )

        # Wait for server to become ready
        for _ in range(10):
            # Check if process exited prematurely
            status = proc.poll()
            if status is not None:
                print(f"Ollama process crashed with exit code {status}")
                return False

            # Check server status
            try:
                response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
                if response.status_code == 200:
                    SERVER_STARTED = True
                    return True
                print(f"Ollama API responded with HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"API connection failed: {str(e)}")

            time.sleep(5)

        # Server didn't start in time - terminate process group
        print("Ollama didn't start within timeout. Killing process group...")
        try:
            pgid = os.getpgid(proc.pid)
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            print("Process already terminated")
        return False

    except Exception as e:
        print(f"Server start failed: {str(e)}")
        return False


def getData(event) -> Optional[Tuple[str, str, Dict[str, Dict[str, Dict[str, str]]]]]:
    try:
        print("Raw Body: ", event.get("Records")[0]["body"])
        print(
            "Event Body is: ",
            json.loads(event.get("Records")[0]["body"]),
        )
        body: Dict[str, str] = json.loads(event.get("Records")[0]["body"])
        print("Body is: ", body)
        query: str = body.get("query")
        processing_id: str = body.get("processing_id")
        documents: Dict[str, Dict[str, str]] = body.get("documents")
        return processing_id, query, documents
    except Exception as e:
        print("Error: ", e)
        return None, None, None


def generateResponse(
    query: str, documents: Dict[str, Dict[str, Dict[str, str]]]
) -> str:
    context: List[str] = [document["document"] for document in documents.values()]

    model: OllamaLLM = OllamaLLM(model="llama3.1")
    prompt: str = f"""<｜begin▁of▁sentence｜>Human:
    [INST] You are an expert AI assistant. Carefully analyze the provided context to answer the question.
    Your response must be:
    - Factual and precise
    - Based ONLY on the given context
    - In clear English paragraphs
    - With citations from context when possible
    - If you do not know the answer based on the context, say "I don't know" [/INST]

    ### Context:
    {context}

    ### Question:
    {query}

    <｜begin▁of▁sentence｜>Assistant: """

    return model.invoke(input=prompt)


def handler(event, context):

    dynamodb = boto3.client(service_name="dynamodb", region_name="us-east-1")
    (process_id, query, documents) = getData(event=event)
    if not start_ollama_server():
        dynamodb.put_item(
            Item={
                "processing_id": {"S": process_id},
                "status": {"S": "ERROR"},
                "error": {"S": "Unable to start the inference model"},
            },
            TableName=TABLE_NAME,
            ReturnConsumedCapacity="Total",
        )
        return dict(statusCode=500, error="Ollama server failed to start")

    if query is None or documents is None or process_id is None:
        print(f"Query is: {query} and its type is {type(query)}")
        print(f"Documents is: {documents} and its type is {type(documents)}")
        dynamodb.put_item(
            Item={
                "processing_id": {"S": process_id},
                "status": {"S": "ERROR"},
                "error": {
                    "S": "One of the values to the function was not provided correctly"
                },
            },
            TableName=TABLE_NAME,
            ReturnConsumedCapacity="Total",
        )

        return dict(
            statusCode=422,
            error="One of the required parameter 'query' or 'documents' is missing",
        )

    response: str = generateResponse(query=query, documents=documents)
    print("Response is:", response)

    # Store it in dyanmo db
    dynamodb.put_item(
        Item={
            "processing_id": {"S": process_id},
            "status": {"S": "COMPLETED"},
            "result": {"S": response},
        },
        TableName=TABLE_NAME,
        ReturnConsumedCapacity="TOTAL",
    )

    return dict(statusCode=200, response="Stored the response in DynamoDB", error=None)
