import boto3
from moto import mock_kinesis
from config import *
import sys
from botocore.exceptions import ClientError

aws_key_id = accesskeyid
aws_key = secretaccesskey


def delete_stream(client, stream_name):
    try:
        print("Successfully delete kinesis stream: {}".format(stream_name))
        return client.delete_delivery_stream(DeliveryStreamName=stream_name)
    except:
        print("Kinesis {} does not exist".format(stream_name))


def main(stream_name):
    client = boto3.client("firehose", region_name="us-east-1",
                          aws_access_key_id=aws_key_id,
                          aws_secret_access_key=aws_key
                          )
    delete_stream(client, stream_name)


if __name__ == '__main__':
    main(sys.argv[1])
