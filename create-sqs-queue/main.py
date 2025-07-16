import boto3

if __name__ == "__main__":
    sqs_client = boto3.client(
        service_name="sqs",
        endpoint_url="http://elastic-mq:9324",
        region_name="elasticmq",
        aws_access_key_id="XXXX",
        aws_secret_access_key="XXXX",
    )

    # Create Chunker Queue
    sqs_client.create_queue(QueueName="chunker-queue")
    print("INFO: Created Chunker Queue")

    # Create Submit Request Queue
    sqs_client.create_queue(QueueName="submit-request-queue")
    print("INFO: Create Submit Request Queue")
