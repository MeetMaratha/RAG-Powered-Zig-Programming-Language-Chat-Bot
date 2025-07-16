import time

import boto3

if __name__ == "__main__":
    time.sleep(20)

    dynamo_db_client = boto3.client(
        service_name="dynamodb",
        endpoint_url="http://dynamo-db:8000",
        region_name="elasticmq",
        aws_access_key_id="XXXX",
        aws_secret_access_key="XXXX",
    )

    # Create Chunker Queue
    dynamo_db_client.create_table(
        TableName="response-table",
        AttributeDefinitions=[
            {
                "AttributeName": "processing_id",
                "AttributeType": "S",
            },
        ],
        KeySchema=[
            {
                "AttributeName": "processing_id",
                "KeyType": "HASH",
            },
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )
    print("INFO: Created Response Table in DynamoDB")

    response = dynamo_db_client.list_tables(Limit=5)

    print("Tables in the DynamoDB:")
    print(response)
