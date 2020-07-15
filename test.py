import boto3
from config import *
import json
import plotly.graph_objects as go

if __name__ == '__main__':
    sqs = boto3.client('sqs', aws_access_key_id=accesskeyid,
                       aws_secret_access_key=secretaccesskey,
                       region_name=region)

    resp = sqs.receive_message(
        QueueUrl=hashtag_queue_url,
        AttributeNames=['All'],
        MaxNumberOfMessages=1
    )

    try:
        messages = resp['Messages']
        message = messages[0]
        string_body_dictionary = message['Body']
        body_dictionary = json.loads(string_body_dictionary)
        string_message_dictionary = body_dictionary.get('Message')
        hashtag_dictionary = json.loads(string_message_dictionary)

        labels = []
        values = []

        for hashtag_labels in hashtag_dictionary:
            labels.append(hashtag_labels)

        for hashtag_values in hashtag_dictionary.values():
            values.append(hashtag_values)

        fig = go.Figure([go.Bar(x=labels, y=values)])
        fig.show()


    except KeyError:
        print("error")
