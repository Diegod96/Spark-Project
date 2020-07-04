from tweepy import Stream, OAuthHandler
from tweepy.streaming import StreamListener
import json
import boto3
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
from config import *


# Instantiate vaderSentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Credentials for Twitter & AWS
consumer_key = ckey
consumer_secret = csecret
access_token = atoken
access_token_secret = atokensecret
aws_key_id = accesskeyid
aws_key = secretaccesskey


def sentiment_analysis(text):
    """
    Performs sentiment analysis on tweet text
    :param text:
    :return: sentiment
    """
    vs = analyzer.polarity_scores(text)
    sentiment = str(vs['compound'])
    return sentiment


class TweetStreamListener(StreamListener):

    def on_data(self, data):
        """
        Picks out english language tweets and parses them up into a dictionary of the tweet's timestamp, text,
        and sentiment score
        :param data:
        :return:
        """
        all_data = json.loads(data)
        tweet_data = {}
        try:
            if 'lang' in all_data and (all_data['lang'] == "en"):
                tweet_data['ts'] = str(all_data["timestamp_ms"])
                # tweet_data['status_id'] = str(all_data["id"])
                tweet_data['text'] = unidecode(all_data["text"])
                tweet_data['sentiment'] = str(sentiment_analysis(all_data["text"]))
                kinesis_client.put_record(
                    DeliveryStreamName=stream_name,
                    Record={
                        'Data': json.dumps(tweet_data) + '\n'
                    }
                )
                print(tweet_data)
        except (AttributeError, Exception) as e:
            print(e)
        return True

    def on_error(self, status):
        """
        Return an status code error
        :param status:
        :return:
        """
        print(status)


if __name__ == '__main__':
    kinesis_client = boto3.client('firehose',
                                  region_name=region,  # enter the region
                                  aws_access_key_id=accesskeyid,  # fill your AWS access key id
                                  aws_secret_access_key=secretaccesskey)  # fill you aws secret access key
    listener = TweetStreamListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)
    stream.filter(track=["a", "e", "i", "o", "u"])