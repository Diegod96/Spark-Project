import boto3
import json
import copy
from config import *

previous_data = []

def get_message():
    global previous_data
    sqs = boto3.client('sqs', aws_access_key_id=accesskeyid,
                       aws_secret_access_key=secretaccesskey,
                       region_name=region)

    while True:
        resp = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1
        )

        try:
            data = []
            messages = resp['Messages']
            message = messages[0]
            string_body_dictionary = message['Body']
            body_dictionary = json.loads(string_body_dictionary)
            string_message_dictionary = body_dictionary.get('Message')
            sentiment_dictionary = json.loads(string_message_dictionary)
            positive = sentiment_dictionary.get('Positive')
            negative = sentiment_dictionary.get('Negative')
            neutral = sentiment_dictionary.get('Neutral')
            data.append(positive)
            data.append(negative)
            data.append(neutral)
            entries = [
                {'Id': msg['MessageId'], 'ReceiptHandle': msg['ReceiptHandle']}
                for msg in resp['Messages']
            ]

            resp = sqs.delete_message_batch(
                QueueUrl=queue_url, Entries=entries
            )

            if len(resp['Successful']) != len(entries):
                raise RuntimeError(
                    f"Failed to delete messages: entries={entries!r} resp={resp!r}"
                )
            return data
        except KeyError:
            break




if __name__ == '__main__':
    x = get_message()
    y = copy.deepcopy(x)
    print(y)
