import boto3
from config import *
import sys


aws_key_id = accesskeyid
aws_key = secretaccesskey


def delete_stream(client, stream_name):
    """
    Deletes Kinesis Firehose stream
    :param client:
    :param stream_name:
    :return:
    """
    try:
        print("Successfully delete kinesis stream: {}".format(stream_name))
        return client.delete_delivery_stream(DeliveryStreamName=stream_name)
    except:
        print("Kinesis {} does not exist".format(stream_name))


def main(stream_name):
    """
    Connects to Kinesis Firehose
    :param stream_name:
    :return:
    """
    client = boto3.client("firehose", region_name="us-east-1",
                          aws_access_key_id=aws_key_id,
                          aws_secret_access_key=aws_key
                          )
    delete_stream(client, stream_name)


if __name__ == '__main__':
    main(sys.argv[1])
