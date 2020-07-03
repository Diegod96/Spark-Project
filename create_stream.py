import boto3
import time
import sys
from moto import mock_kinesis
from config import *
from botocore.exceptions import ClientError

aws_key_id = accesskeyid
aws_key = secretaccesskey


def create_stream(client, stream_name):
    return client.create_delivery_stream(
        DeliveryStreamName=stream_name,
        S3DestinationConfigureation={
            'RoleARN': 'arn:aws:iam::743362587039:role/service-role/KinesisFirehoseServiceRole-diego-tweets--us-east-1-1593268563236',
            'BucketARN': 'arn:aws:s3:::diego-twitter-stream-sink',
            'Prefix': stream_name + '//'
        }
    )


def main(search_name):
    stream_name = search_name[0]
    client = boto3.client('firehose', region_name="us-east-1",
                          aws_access_key_id=aws_key_id,
                          aws_secret_access_key=aws_key
                          )

    try:
        create_stream(client, stream_name)
        print("Creating Kinesis Firehose stream...")
        time.sleep(60)
    except:
        pass

    stream_status = client.describe_delivery_stream(DeliveryStreamName=stream_name)
    if stream_status['DeliveryStreamDescription']['DeliveryStreamStatus'] == 'ACTIVE':
        print("\n ==== KINESES ONLINE ====")


if __name__ == '__main__':
    main("trump")
